#!/usr/bin/env bash
# auto_mutation.sh — PostToolUse Hook for Claude Code
# Part of cq-engine (Cognitive Quality Engineering)
#
# Trigger: After Task tool completion
# Purpose: Automatically run MutaDoc quick-check on modified files
# Protocol: Reads JSON from stdin, writes JSON to stdout
# Safety: Always approves. Mutation results are informational only.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CQ_ENGINE_ROOT="${CQ_ENGINE_ROOT:-$(cd "$SCRIPT_DIR/../../.." 2>/dev/null && pwd)}"
MUTADOC_PATH="${CQ_ENGINE_ROOT}/mutadoc/mutadoc.sh"
TIMEOUT_SECONDS=30

# --- Helpers ---

approve() {
    local reason="${1:-OK}"
    printf '{"decision":"approve","reason":"%s"}\n' "$reason"
    exit 0
}

log() {
    echo "[cq-mutation] $*" >&2
}

# --- Main ---

# Read stdin
INPUT=$(cat)

# Check for jq
if ! command -v jq >/dev/null 2>&1; then
    approve "jq not available, skipping mutation check"
fi

# Extract tool output
TOOL_OUTPUT=$(echo "$INPUT" | jq -r '.tool_output // empty' 2>/dev/null) || true

if [[ -z "$TOOL_OUTPUT" ]]; then
    approve "No tool output to analyze"
fi

# Check if mutadoc.sh exists
if [[ ! -x "$MUTADOC_PATH" ]]; then
    log "mutadoc.sh not found at $MUTADOC_PATH"
    approve "MutaDoc not available, skipping mutation check"
fi

# Extract file paths from tool output
# Look for patterns like: /path/to/file.md, /path/to/file.yaml, etc.
MODIFIED_FILES=$(echo "$TOOL_OUTPUT" | grep -oE '(/[a-zA-Z0-9_./-]+\.(md|yaml|yml|txt|json))' 2>/dev/null | sort -u || true)

if [[ -z "$MODIFIED_FILES" ]]; then
    approve "No modified files detected in output"
fi

# Run mutadoc quick-check on each file
TOTAL_SURVIVING=0
FILES_CHECKED=0
FILE_RESULTS=""

while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ ! -f "$file" ]] && continue

    log "Checking: $file"
    FILES_CHECKED=$((FILES_CHECKED + 1))

    # Run mutadoc with timeout
    RESULT=""
    if command -v timeout >/dev/null 2>&1; then
        RESULT=$(timeout "$TIMEOUT_SECONDS" "$MUTADOC_PATH" quick "$file" 2>/dev/null) || true
    else
        RESULT=$("$MUTADOC_PATH" quick "$file" 2>/dev/null) || true
    fi

    if [[ -n "$RESULT" ]]; then
        # Extract surviving mutation count from result
        SURVIVING=$(echo "$RESULT" | grep -oE '[0-9]+ surviving' | grep -oE '[0-9]+' || echo "0")
        SURVIVING=${SURVIVING:-0}
        TOTAL_SURVIVING=$((TOTAL_SURVIVING + SURVIVING))

        if [[ -n "$FILE_RESULTS" ]]; then
            FILE_RESULTS="${FILE_RESULTS}, $(basename "$file"): ${SURVIVING}"
        else
            FILE_RESULTS="$(basename "$file"): ${SURVIVING}"
        fi
    fi
done <<< "$MODIFIED_FILES"

if [[ $FILES_CHECKED -eq 0 ]]; then
    approve "No existing files to check"
fi

if [[ $TOTAL_SURVIVING -gt 0 ]]; then
    approve "Mutation check: ${TOTAL_SURVIVING} surviving mutations in ${FILES_CHECKED} file(s) [${FILE_RESULTS}]"
else
    approve "Mutation check passed: 0 surviving mutations in ${FILES_CHECKED} file(s)"
fi
