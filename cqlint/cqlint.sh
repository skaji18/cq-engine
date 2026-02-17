#!/usr/bin/env bash
# cqlint — Cognitive Quality Linter for LLM Agent Configurations
# Part of cq-engine (Cognitive Quality Engineering)
# Version: 0.1.0
# License: MIT
#
# Zero Infrastructure: Bash + standard UNIX tools only.
# Every rule maps to a CQE Pattern. No arbitrary style checks.

set -euo pipefail

VERSION="0.1.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Colors ---
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
GRAY='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- Globals ---
FORMAT="text"
RULE_FILTER=""
ERRORS=0
WARNINGS=0
SKIPS=0
PASSES=0
JSON_RESULTS="[]"
TARGET=""

# ============================================================
# Help
# ============================================================
show_help() {
    cat <<'HELP'
cqlint — Cognitive Quality Linter for LLM Agent Configurations

USAGE:
    cqlint check <path>              Check a file or directory
    cqlint check <path> --rule CQ001 Run a specific rule only
    cqlint check <path> --format json Output as JSON
    cqlint --help                    Show this help
    cqlint --version                 Show version

RULES:
    CQ001  attention-budget-missing    Task lacks token budget       [WARNING]
    CQ002  context-contamination-risk  No filtering between stages   [ERROR]
    CQ003  generic-persona             Persona is generic/missing    [WARNING]
    CQ004  no-mutation-on-critical     Critical task has no review   [ERROR]
    CQ005  learning-disabled           No learning mechanism         [WARNING]

EXAMPLES:
    cqlint check ./my-agent-project/
    cqlint check task.yaml --rule CQ001
    cqlint check . --format json

Each rule maps to a CQE Pattern. See cqlint/rules/ for detailed documentation.
HELP
}

# ============================================================
# Output helpers
# ============================================================
emit_error() {
    local rule="$1" file="$2" line="$3" msg="$4" hint="$5"
    ERRORS=$((ERRORS + 1))
    if [[ "$FORMAT" == "json" ]]; then
        JSON_RESULTS=$(echo "$JSON_RESULTS" | sed 's/]$//')
        [[ "$JSON_RESULTS" != "[" ]] && JSON_RESULTS="${JSON_RESULTS},"
        JSON_RESULTS="${JSON_RESULTS}{\"rule\":\"${rule}\",\"severity\":\"ERROR\",\"file\":\"${file}\",\"line\":${line},\"message\":\"${msg}\"}]"
    else
        echo -e "  ${RED}ERROR${NC} ${BOLD}${rule}${NC}: ${file}:${line} — ${msg}"
        echo -e "    ${GRAY}→ ${hint}${NC}"
    fi
}

emit_warning() {
    local rule="$1" file="$2" line="$3" msg="$4" hint="$5"
    WARNINGS=$((WARNINGS + 1))
    if [[ "$FORMAT" == "json" ]]; then
        JSON_RESULTS=$(echo "$JSON_RESULTS" | sed 's/]$//')
        [[ "$JSON_RESULTS" != "[" ]] && JSON_RESULTS="${JSON_RESULTS},"
        JSON_RESULTS="${JSON_RESULTS}{\"rule\":\"${rule}\",\"severity\":\"WARNING\",\"file\":\"${file}\",\"line\":${line},\"message\":\"${msg}\"}]"
    else
        echo -e "  ${YELLOW}WARNING${NC} ${BOLD}${rule}${NC}: ${file}:${line} — ${msg}"
        echo -e "    ${GRAY}→ ${hint}${NC}"
    fi
}

emit_pass() {
    local rule="$1" file="$2"
    PASSES=$((PASSES + 1))
}

emit_skip() {
    local rule="$1" file="$2"
    SKIPS=$((SKIPS + 1))
}

# ============================================================
# File discovery
# ============================================================
find_yaml_files() {
    local target="$1"
    if [[ -f "$target" ]]; then
        echo "$target"
    elif [[ -d "$target" ]]; then
        find "$target" -type f \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort
    fi
}

# ============================================================
# Rule: CQ001 — attention-budget-missing
# Pattern: #01 Attention Budget
# ============================================================
check_CQ001() {
    local file="$1"
    local rule="CQ001"

    # Check if this is a task definition file.
    # A task definition has "task:" as a top-level key with sub-keys (name, description, etc.)
    # Exclude files where "task:" is just a field value (e.g., "task: do something" inside an agent block)
    if ! grep -qE '^task\s*:' "$file" 2>/dev/null; then
        emit_skip "$rule" "$file"
        return
    fi

    # Verify it's a real task block (has indented sub-keys like name/description)
    if ! grep -qE '^\s+(name|description|task_id)\s*:' "$file" 2>/dev/null; then
        emit_skip "$rule" "$file"
        return
    fi

    # Look for budget-related fields
    if grep -qEi '(attention_budget|token_budget|budget|max_tokens|token_limit|context_limit)\s*:' "$file" 2>/dev/null; then
        # Check if value is null or 0
        local budget_line
        budget_line=$(grep -nEi '(attention_budget|token_budget|budget|max_tokens|token_limit|context_limit)\s*:' "$file" | head -1)
        local line_num
        line_num=$(echo "$budget_line" | cut -d: -f1)
        local value
        value=$(echo "$budget_line" | sed 's/.*:\s*//')

        if [[ "$value" == "null" || "$value" == "0" ]]; then
            emit_warning "$rule" "$file" "$line_num" \
                "Attention budget is set to null/zero." \
                "Pattern #01 (Attention Budget): Set an explicit non-zero token budget."
        else
            # Value is non-empty and non-null, or it's a YAML mapping (empty = sub-keys follow)
            emit_pass "$rule" "$file"
        fi
    else
        # Find the task definition line for reporting
        local task_line
        task_line=$(grep -nE '^task\s*:' "$file" | head -1 | cut -d: -f1)
        emit_warning "$rule" "$file" "${task_line:-1}" \
            "Task has no attention budget defined." \
            "Pattern #01 (Attention Budget): Set an explicit token budget before execution."
    fi
}

# ============================================================
# Rule: CQ002 — context-contamination-risk
# Pattern: #02 Context Gate
# ============================================================
check_CQ002() {
    local file="$1"
    local rule="CQ002"

    # Check if this is a pipeline/multi-stage definition
    if ! grep -qEi '(pipeline|stages|depends_on|workflow)\s*:' "$file" 2>/dev/null; then
        emit_skip "$rule" "$file"
        return
    fi

    # Check if there are stage transitions (depends_on references)
    if ! grep -qEi 'depends_on\s*:' "$file" 2>/dev/null; then
        emit_skip "$rule" "$file"
        return
    fi

    # Look for filtering directives
    if grep -qEi '(context_filter|context_gate|gate\s*:|filter\s*:|output_scope|input_scope|select\s*:|include_only)\s*:' "$file" 2>/dev/null; then
        emit_pass "$rule" "$file"
    else
        local dep_line
        dep_line=$(grep -nEi 'depends_on\s*:' "$file" | head -1 | cut -d: -f1)
        emit_error "$rule" "$file" "${dep_line:-1}" \
            "Multi-stage pipeline has no context filtering between stages." \
            "Pattern #02 (Context Gate): Add context_gate or input_scope between stages."
    fi
}

# ============================================================
# Rule: CQ003 — generic-persona
# Pattern: #03 Cognitive Profile
# ============================================================
check_CQ003() {
    local file="$1"
    local rule="CQ003"

    # Check if this is an agent definition
    if ! grep -qEi '(agent|persona|role|system_prompt|cognitive_profile)\s*:' "$file" 2>/dev/null; then
        emit_skip "$rule" "$file"
        return
    fi

    # Look for persona-related fields
    local persona_value=""
    local persona_line="1"

    if grep -qEi '(persona|cognitive_profile|system_prompt)\s*:' "$file" 2>/dev/null; then
        local match
        match=$(grep -nEi '(persona|cognitive_profile|system_prompt)\s*:' "$file" | head -1)
        persona_line=$(echo "$match" | cut -d: -f1)
        # Extract value after the key (handle both "key: value" and "key: 'value'")
        persona_value=$(echo "$match" | sed 's/^[^:]*:[^:]*:\s*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//' | xargs)
    fi

    # No persona field found
    if [[ -z "$persona_value" ]]; then
        # Check if file has agent-like structure but no persona
        if grep -qEi '(agent|role)\s*:' "$file" 2>/dev/null; then
            local agent_line
            agent_line=$(grep -nEi '(agent|role)\s*:' "$file" | head -1 | cut -d: -f1)
            emit_warning "$rule" "$file" "${agent_line:-1}" \
                "Agent has no persona defined." \
                "Pattern #03 (Cognitive Profile): Define a domain-specific persona."
        else
            emit_skip "$rule" "$file"
        fi
        return
    fi

    # Check for file reference (always pass)
    if echo "$persona_value" | grep -qE '\.(md|txt|yaml|yml|json)$'; then
        emit_pass "$rule" "$file"
        return
    fi

    # Check for generic keywords
    local generic_patterns="^(assistant|helper|bot|ai|agent|general|default)$"
    local generic_phrases="you are a helpful|you are an ai|you are a general"
    local lower_value
    lower_value=$(echo "$persona_value" | tr '[:upper:]' '[:lower:]')

    if echo "$lower_value" | grep -qEi "$generic_patterns"; then
        emit_warning "$rule" "$file" "$persona_line" \
            "Agent persona is generic: \"${persona_value}\"." \
            "Pattern #03 (Cognitive Profile): Replace with a domain-specific persona."
        return
    fi

    if echo "$lower_value" | grep -qEi "$generic_phrases"; then
        emit_warning "$rule" "$file" "$persona_line" \
            "Agent persona uses a generic phrase: \"${persona_value}\"." \
            "Pattern #03 (Cognitive Profile): Replace with a domain-specific persona."
        return
    fi

    # Check minimum length
    if [[ ${#persona_value} -lt 20 ]]; then
        emit_warning "$rule" "$file" "$persona_line" \
            "Agent persona is too short (${#persona_value} chars): \"${persona_value}\"." \
            "Pattern #03 (Cognitive Profile): Expand with expertise and behavioral traits."
        return
    fi

    emit_pass "$rule" "$file"
}

# ============================================================
# Rule: CQ004 — no-mutation-on-critical
# Pattern: #05 Assumption Mutation
# ============================================================
check_CQ004() {
    local file="$1"
    local rule="CQ004"

    # Check if this file has risk-level indicators
    local risk_match=""
    risk_match=$(grep -nEi '(danger_level|priority|risk|criticality)\s*:\s*(high|critical)' "$file" 2>/dev/null | head -1 || true)

    if [[ -z "$risk_match" ]]; then
        emit_skip "$rule" "$file"
        return
    fi

    local risk_line
    risk_line=$(echo "$risk_match" | cut -d: -f1)

    # Look for verification mechanisms as YAML keys/values (not in free-text descriptions)
    # Match patterns like "mutation: true", "review: enabled", "gate_required: true",
    # "adversarial: true", "verify: true" — i.e., key-value pairs, not prose.
    if grep -qEi '^\s*(mutation|mutate|mutation_test|peer_review|verify|verification|adversarial)\s*:' "$file" 2>/dev/null; then
        emit_pass "$rule" "$file"
        return
    fi

    # Check for gate_required: true
    if grep -qEi '^\s*gate_required\s*:\s*true' "$file" 2>/dev/null; then
        emit_pass "$rule" "$file"
        return
    fi

    # Check depends_on for review/verify/test/mutation task references
    if grep -qEi 'depends_on.*\b(review|verify|test|mutation)\b' "$file" 2>/dev/null; then
        emit_pass "$rule" "$file"
        return
    fi

    emit_error "$rule" "$file" "${risk_line:-1}" \
        "High-risk task has no mutation or verification step." \
        "Pattern #05 (Assumption Mutation): Add mutation testing or adversarial review."
}

# ============================================================
# Rule: CQ005 — learning-disabled
# Pattern: #06 Experience Distillation
# ============================================================
check_CQ005() {
    local file="$1"
    local rule="CQ005"

    # This is a project-level check — look for project/config indicators
    if ! grep -qEi '(project|config|settings)\s*:' "$file" 2>/dev/null; then
        emit_skip "$rule" "$file"
        return
    fi

    # Check for learning-related configuration fields
    if grep -qEi '(learning|experience_distillation|memory|feedback)\s*:\s*(enabled|true)' "$file" 2>/dev/null; then
        emit_pass "$rule" "$file"
        return
    fi

    # Check for memory_path or similar
    if grep -qEi '(memory_path|learned_path|knowledge_path|experience_path)\s*:' "$file" 2>/dev/null; then
        emit_pass "$rule" "$file"
        return
    fi

    # Check if learning is explicitly disabled
    if grep -qEi '(learning|feedback)\s*:\s*(false|disabled)' "$file" 2>/dev/null; then
        local disable_line
        disable_line=$(grep -nEi '(learning|feedback)\s*:\s*(false|disabled)' "$file" | head -1 | cut -d: -f1)
        emit_warning "$rule" "$file" "${disable_line:-1}" \
            "Learning mechanism is explicitly disabled." \
            "Pattern #06 (Experience Distillation): Enable learning to prevent repeated failures."
        return
    fi

    # No learning mechanism found
    local project_line
    project_line=$(grep -nEi '(project|config|settings)\s*:' "$file" | head -1 | cut -d: -f1)
    emit_warning "$rule" "$file" "${project_line:-1}" \
        "No learning mechanism configured." \
        "Pattern #06 (Experience Distillation): Add memory/ directory or learning: enabled."
}

# ============================================================
# Directory-level CQ005 check
# ============================================================
check_CQ005_directory() {
    local target="$1"
    local rule="CQ005"

    [[ ! -d "$target" ]] && return

    # Check for learning directories
    local learning_dirs=("memory" "learned" "experience" "knowledge" "learnings" "lp")
    for dir in "${learning_dirs[@]}"; do
        if [[ -d "${target}/${dir}" ]]; then
            local file_count
            file_count=$(find "${target}/${dir}" -type f 2>/dev/null | wc -l)
            if [[ "$file_count" -gt 0 ]]; then
                emit_pass "$rule" "${target}/${dir}/"
                return
            fi
        fi
    done
}

# ============================================================
# Summary
# ============================================================
print_summary() {
    local total=$((ERRORS + WARNINGS + PASSES + SKIPS))

    if [[ "$FORMAT" == "json" ]]; then
        echo "{\"version\":\"${VERSION}\",\"errors\":${ERRORS},\"warnings\":${WARNINGS},\"passes\":${PASSES},\"skipped\":${SKIPS},\"results\":${JSON_RESULTS}}"
        return
    fi

    echo ""
    echo -e "${BOLD}─── cqlint summary ───${NC}"

    if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
        echo -e "  ${GREEN}✓${NC} All checks passed."
    fi

    local parts=()
    [[ $ERRORS -gt 0 ]] && parts+=("${RED}${ERRORS} error(s)${NC}")
    [[ $WARNINGS -gt 0 ]] && parts+=("${YELLOW}${WARNINGS} warning(s)${NC}")
    [[ $PASSES -gt 0 ]] && parts+=("${GREEN}${PASSES} passed${NC}")
    [[ $SKIPS -gt 0 ]] && parts+=("${GRAY}${SKIPS} skipped${NC}")

    echo -e "  $(IFS=', '; echo "${parts[*]}")"
    echo ""
}

# ============================================================
# Main
# ============================================================
main() {
    # Parse arguments
    local command=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            check)
                command="check"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            --version|-v)
                echo "cqlint ${VERSION}"
                exit 0
                ;;
            --rule)
                RULE_FILTER="$2"
                shift 2
                ;;
            --format)
                FORMAT="$2"
                shift 2
                ;;
            *)
                if [[ -z "$TARGET" ]]; then
                    TARGET="$1"
                fi
                shift
                ;;
        esac
    done

    # Validate
    if [[ -z "$command" && -z "$TARGET" ]]; then
        show_help
        exit 0
    fi

    if [[ -z "$TARGET" ]]; then
        echo -e "${RED}Error: No target specified.${NC}" >&2
        echo "Usage: cqlint check <path>" >&2
        exit 2
    fi

    if [[ ! -e "$TARGET" ]]; then
        echo -e "${RED}Error: Target not found: ${TARGET}${NC}" >&2
        exit 2
    fi

    # Header
    if [[ "$FORMAT" == "text" ]]; then
        echo ""
        echo -e "${BOLD}cqlint v${VERSION}${NC} — Cognitive Quality Linter"
        echo -e "Checking: ${BLUE}${TARGET}${NC}"
        echo ""
    fi

    # Collect files
    local files
    files=$(find_yaml_files "$TARGET")

    if [[ -z "$files" ]]; then
        if [[ "$FORMAT" == "text" ]]; then
            echo -e "  ${GRAY}No YAML files found in ${TARGET}${NC}"
        fi
        print_summary
        exit 0
    fi

    # Run directory-level checks first
    if [[ -d "$TARGET" ]]; then
        if [[ -z "$RULE_FILTER" || "$RULE_FILTER" == "CQ005" ]]; then
            check_CQ005_directory "$TARGET"
        fi
    fi

    # Run per-file checks
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue

        if [[ -z "$RULE_FILTER" || "$RULE_FILTER" == "CQ001" ]]; then
            check_CQ001 "$file"
        fi
        if [[ -z "$RULE_FILTER" || "$RULE_FILTER" == "CQ002" ]]; then
            check_CQ002 "$file"
        fi
        if [[ -z "$RULE_FILTER" || "$RULE_FILTER" == "CQ003" ]]; then
            check_CQ003 "$file"
        fi
        if [[ -z "$RULE_FILTER" || "$RULE_FILTER" == "CQ004" ]]; then
            check_CQ004 "$file"
        fi
        if [[ -z "$RULE_FILTER" || "$RULE_FILTER" == "CQ005" ]]; then
            check_CQ005 "$file"
        fi
    done <<< "$files"

    # Summary
    print_summary

    # Exit code
    if [[ $ERRORS -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

main "$@"
