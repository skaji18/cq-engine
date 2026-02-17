#!/usr/bin/env bash
# cognitive_hygiene_check.sh — PreToolUse Hook for Claude Code
# Part of cq-engine (Cognitive Quality Engineering)
#
# Trigger: Before Edit/Write tool execution
# Purpose: Compute a lightweight Context Health Score and warn if below threshold
# Protocol: Reads JSON from stdin, writes JSON to stdout
# Safety: Always approves (never blocks). Warnings only.

set -euo pipefail

CONTEXT_HEALTH_THRESHOLD="${CONTEXT_HEALTH_THRESHOLD:-0.6}"

# --- Helpers ---

# Safe JSON output — always approve, never block Claude Code
approve() {
    local reason="${1:-OK}"
    printf '{"decision":"approve","reason":"%s"}\n' "$reason"
    exit 0
}

log() {
    echo "[cq-hygiene] $*" >&2
}

# Floating point math with bc fallback to integer approximation
calc() {
    if command -v bc >/dev/null 2>&1; then
        echo "$1" | bc -l 2>/dev/null || echo "0"
    else
        # Integer approximation: multiply by 100, do integer math, divide
        # This is a rough fallback for systems without bc
        echo "$1" | awk '{printf "%.2f", $1}' 2>/dev/null || echo "0"
    fi
}

max0() {
    local val="$1"
    if command -v bc >/dev/null 2>&1; then
        local cmp
        cmp=$(echo "$val < 0" | bc -l 2>/dev/null || echo "0")
        if [[ "$cmp" == "1" ]]; then
            echo "0"
        else
            echo "$val"
        fi
    else
        echo "$val" | awk '{if ($1 < 0) print 0; else printf "%.2f", $1}'
    fi
}

# --- Main ---

# Read stdin (JSON from Claude Code)
INPUT=$(cat)

# Check for jq availability
if ! command -v jq >/dev/null 2>&1; then
    approve "jq not available, skipping check"
fi

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || true

if [[ -z "$FILE_PATH" ]]; then
    approve "No file path in tool input"
fi

# --- Compute Context Health Score ---

# 1. File count score: penalize directories with too many files
DIR_PATH=$(dirname "$FILE_PATH" 2>/dev/null) || true
if [[ -d "$DIR_PATH" ]]; then
    DIR_FILE_COUNT=$(find "$DIR_PATH" -maxdepth 1 -type f 2>/dev/null | wc -l)
else
    DIR_FILE_COUNT=0
fi
FILE_COUNT_SCORE=$(max0 "$(calc "1.0 - ($DIR_FILE_COUNT - 5) * 0.05")")

# 2. File size score: penalize very large files
if [[ -f "$FILE_PATH" ]]; then
    FILE_SIZE_BYTES=$(wc -c < "$FILE_PATH" 2>/dev/null || echo "0")
else
    FILE_SIZE_BYTES=0
fi
FILE_SIZE_SCORE=$(max0 "$(calc "1.0 - ($FILE_SIZE_BYTES / 100000.0)")")

# 3. Freshness score: penalize stale files
if [[ -f "$FILE_PATH" ]]; then
    FILE_MOD_EPOCH=$(stat -c %Y "$FILE_PATH" 2>/dev/null || stat -f %m "$FILE_PATH" 2>/dev/null || echo "0")
    NOW_EPOCH=$(date +%s)
    AGE_SECONDS=$((NOW_EPOCH - FILE_MOD_EPOCH))
    SEVEN_DAYS=$((7 * 24 * 3600))
    if [[ $AGE_SECONDS -le $SEVEN_DAYS ]]; then
        FRESHNESS_SCORE=$(calc "1.0 - ($AGE_SECONDS.0 / $SEVEN_DAYS.0) * 0.5")
        FRESHNESS_SCORE=$(max0 "$FRESHNESS_SCORE")
    else
        # Older than 7 days: rapid decay
        FRESHNESS_SCORE=$(max0 "$(calc "0.5 - ($AGE_SECONDS.0 / ($SEVEN_DAYS.0 * 4)) * 0.5")")
    fi
else
    # New file (doesn't exist yet) — perfectly fresh
    FRESHNESS_SCORE="1.0"
fi

# 4. Aggregate health score (clamped to [0.0, 1.0])
HEALTH_SCORE=$(calc "($FILE_COUNT_SCORE + $FILE_SIZE_SCORE + $FRESHNESS_SCORE) / 3.0")
# Clamp to max 1.0
ABOVE_ONE=$(echo "$HEALTH_SCORE > 1.0" | bc -l 2>/dev/null || echo "0")
if [[ "$ABOVE_ONE" == "1" ]]; then
    HEALTH_SCORE="1.00"
fi

log "file=$FILE_PATH count_score=$FILE_COUNT_SCORE size_score=$FILE_SIZE_SCORE fresh_score=$FRESHNESS_SCORE health=$HEALTH_SCORE"

# 5. Compare against threshold
BELOW_THRESHOLD=$(echo "$HEALTH_SCORE < $CONTEXT_HEALTH_THRESHOLD" | bc -l 2>/dev/null || echo "0")

if [[ "$BELOW_THRESHOLD" == "1" ]]; then
    approve "Context health WARNING (score: ${HEALTH_SCORE}, threshold: ${CONTEXT_HEALTH_THRESHOLD}). Directory has ${DIR_FILE_COUNT} files, target file is ${FILE_SIZE_BYTES} bytes. Consider applying Context Gate pattern."
else
    approve "Context health OK (score: ${HEALTH_SCORE})"
fi
