#!/usr/bin/env bash
# auto_learn.sh — Notification Hook for Claude Code
# Part of cq-engine (Cognitive Quality Engineering)
#
# Trigger: Task completion notifications
# Purpose: Automatically extract learning signals and persist them
# Protocol: Reads JSON from stdin, writes nothing to stdout (notification hook)
# Safety: Silent on all errors. Never blocks Claude Code.

set -euo pipefail

LEARN_DIR="${CQ_ENGINE_LEARN_DIR:-${HOME}/.cq-engine/learned}"
LEARN_FILE="${LEARN_DIR}/global.jsonl"

# --- Helpers ---

log() {
    echo "[cq-learn] $*" >&2
}

generate_id() {
    echo "L$(date +%Y%m%d_%H%M%S)_${RANDOM}"
}

get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Classify message into learning category
classify_message() {
    local msg="$1"
    local lower_msg
    lower_msg=$(echo "$msg" | tr '[:upper:]' '[:lower:]')

    # Check for failure signals
    if echo "$lower_msg" | grep -qE '(failed|error|exception|crash|timeout|abort|panic)'; then
        echo "failure"
        return
    fi

    # Check for success/optimization signals
    if echo "$lower_msg" | grep -qE '(success|completed|passed|optimized|improved|resolved)'; then
        echo "optimization"
        return
    fi

    # Check for CQE pattern usage signals
    if echo "$lower_msg" | grep -qE '(attention.?budget|context.?gate|cognitive.?profile|wave.?scheduler|assumption.?mutation|experience.?distillation|file.?based|template.?driven|cqlint|mutadoc|thinktank|cqe)'; then
        echo "pattern_usage"
        return
    fi

    # Default: preference
    echo "preference"
}

# Extract a concise observation from the message
extract_observation() {
    local msg="$1"
    # Truncate to 200 chars for storage efficiency
    echo "$msg" | head -c 200 | tr '"' "'" | tr '\n' ' ' | sed 's/[[:space:]]*$//'
}

# --- Main ---

# Read stdin
INPUT=$(cat 2>/dev/null) || true

if [[ -z "$INPUT" ]]; then
    exit 0
fi

# Extract message — try jq first, fall back to grep
MESSAGE=""
if command -v jq >/dev/null 2>&1; then
    MESSAGE=$(echo "$INPUT" | jq -r '.message // empty' 2>/dev/null) || true
fi

# Fallback: extract message without jq
if [[ -z "$MESSAGE" ]]; then
    MESSAGE=$(echo "$INPUT" | grep -oP '"message"\s*:\s*"\K[^"]+' 2>/dev/null) || true
fi

if [[ -z "$MESSAGE" ]]; then
    exit 0
fi

# Classify and extract
CATEGORY=$(classify_message "$MESSAGE")
OBSERVATION=$(extract_observation "$MESSAGE")
LEARN_ID=$(generate_id)
TIMESTAMP=$(get_timestamp)

log "category=$CATEGORY observation=${OBSERVATION:0:50}..."

# Ensure learn directory exists
mkdir -p "$LEARN_DIR" 2>/dev/null || true

# Write learning entry (JSONL format — one JSON object per line)
# Use printf to avoid issues with special characters
if command -v jq >/dev/null 2>&1; then
    jq -n -c \
        --arg id "$LEARN_ID" \
        --arg obs "$OBSERVATION" \
        --arg cat "$CATEGORY" \
        --arg ts "$TIMESTAMP" \
        '{id: $id, observation: $obs, category: $cat, confidence: 0.5, timestamp: $ts, source: "auto_learn_hook"}' \
        >> "$LEARN_FILE" 2>/dev/null || true
else
    # Fallback without jq — manual JSON construction
    printf '{"id":"%s","observation":"%s","category":"%s","confidence":0.5,"timestamp":"%s","source":"auto_learn_hook"}\n' \
        "$LEARN_ID" \
        "$OBSERVATION" \
        "$CATEGORY" \
        "$TIMESTAMP" \
        >> "$LEARN_FILE" 2>/dev/null || true
fi

log "Wrote learning entry $LEARN_ID ($CATEGORY) to $LEARN_FILE"

# Notification hooks produce no stdout
exit 0
