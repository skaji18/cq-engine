#!/usr/bin/env bash
# mutadoc — Mutation Testing for Documents
# Part of cq-engine (Cognitive Quality Engineering)
# Version: 0.1.0
# License: MIT
#
# Zero Infrastructure: Bash + standard UNIX tools only.
# No LLM API calls. Static analysis of document structure and language.

set -uo pipefail

VERSION="0.1.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Colors ---
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m'

# --- Globals ---
SUBCMD=""
DOCUMENT=""
PRESET=""
STRATEGIES=""
PERSONA=""
REPAIR=false
OUTPUT=""
FORMAT="markdown"

TOTAL_MUTATIONS=0
KILLED_MUTATIONS=0
CRITICAL_COUNT=0
MAJOR_COUNT=0
MINOR_COUNT=0
DEAD_CLAUSE_COUNT=0

declare -a FINDINGS=()

# ============================================================
# Vague modifier catalog (S2 Ambiguity)
# ============================================================
VAGUE_MODIFIERS=(
    "reasonable" "appropriate" "adequate" "sufficient" "significant"
    "material" "substantial" "timely" "promptly" "periodically"
    "regularly" "as soon as possible" "best efforts" "commercially reasonable"
    "good faith" "industry standard" "state of the art"
    "including but not limited to" "generally" "primarily"
    "as needed" "to the extent possible" "approximately" "suitable"
    "proper" "satisfactory" "acceptable" "fair" "moderate"
)

# Claim/assumption indicators (S4 Inversion)
CLAIM_INDICATORS=(
    "shall" "must" "will" "requires" "assumes" "ensures"
    "guarantees" "certifies" "warrants" "represents"
    "acknowledges" "agrees" "commits" "obligated"
)

# ============================================================
# Help & Version
# ============================================================
show_help() {
    cat <<'HELP'
mutadoc — Mutation Testing for Documents
Part of cq-engine (Cognitive Quality Engineering)

USAGE:
    mutadoc test <document>              Full mutation test
    mutadoc test <document> --preset P   Use preset configuration
    mutadoc test <document> --strategies S1,S2  Select strategies
    mutadoc test <document> --persona P  Apply persona lens
    mutadoc test <document> --repair     Include repair suggestions
    mutadoc quick <document>             Quick mode (ambiguity only)
    mutadoc score <document>             Mutation Kill Score only
    mutadoc --help                       Show this help
    mutadoc --version                    Show version

STRATEGIES:
    contradiction    S1: Detect cross-section contradictions
    ambiguity        S2: Expose vague modifiers with extreme-value testing
    deletion         S3: Find dead clauses via structural impact analysis
    inversion        S4: Test argument robustness by reversing claims
    boundary         S5: Analyze numeric parameter sensitivity
    all              Run all 5 strategies

PRESETS:
    contract         Legal contracts (opposing_counsel persona)
    api_spec         API specifications (naive_implementer persona)
    academic_paper   Academic papers (adversarial_reader persona)
    policy           Policy documents (adversarial_reader persona)

PERSONAS:
    adversarial_reader    Actively misinterprets to find exploits
    opposing_counsel      Legal adversary seeking contract weaknesses
    naive_implementer     Literal reader who implements exactly what's written

OPTIONS:
    --preset <name>       Apply preset configuration
    --strategies <list>   Comma-separated strategy names, or "all"
    --persona <name>      Apply persona lens to findings
    --repair              Include repair suggestions for each finding
    --output <file>       Write report to file (default: stdout)
    --format <fmt>        Output format: markdown (default), text, json
    --help                Show this help
    --version             Show version

EXIT CODES:
    0    All pass (no Critical or Major findings)
    1    One or more Critical or Major findings
    2    Argument error or file not found

EXAMPLES:
    mutadoc test contract.md --preset contract --repair
    mutadoc quick api_spec.md
    mutadoc test policy.md --strategies ambiguity,contradiction
    mutadoc score document.md --format json
HELP
}

show_version() {
    echo "mutadoc ${VERSION}"
}

# ============================================================
# Argument parsing
# ============================================================
parse_args() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 2
    fi

    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
        test|quick|score)
            SUBCMD="$1"
            shift
            ;;
        *)
            echo -e "${RED}Error${NC}: Unknown command '$1'. Use 'mutadoc --help' for usage."
            exit 2
            ;;
    esac

    if [[ $# -eq 0 ]]; then
        echo -e "${RED}Error${NC}: No document specified. Usage: mutadoc ${SUBCMD} <document>"
        exit 2
    fi

    DOCUMENT="$1"
    shift

    if [[ ! -f "$DOCUMENT" ]]; then
        echo -e "${RED}Error${NC}: File not found: ${DOCUMENT}"
        exit 2
    fi

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --preset)
                PRESET="$2"
                shift 2
                ;;
            --strategies)
                STRATEGIES="$2"
                shift 2
                ;;
            --persona)
                PERSONA="$2"
                shift 2
                ;;
            --repair)
                REPAIR=true
                shift
                ;;
            --output)
                OUTPUT="$2"
                shift 2
                ;;
            --format)
                FORMAT="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Error${NC}: Unknown option '$1'. Use 'mutadoc --help' for usage."
                exit 2
                ;;
        esac
    done

    # Subcommand defaults
    case "$SUBCMD" in
        quick)
            STRATEGIES="ambiguity"
            REPAIR=false
            ;;
        score)
            [[ -z "$STRATEGIES" ]] && STRATEGIES="all"
            ;;
        test)
            [[ -z "$STRATEGIES" ]] && STRATEGIES="all"
            ;;
    esac
}

# ============================================================
# Preset loading
# ============================================================
load_preset() {
    local preset_name="$1"
    local preset_file="${SCRIPT_DIR}/presets/${preset_name}.md"

    if [[ ! -f "$preset_file" ]]; then
        echo -e "${RED}Error${NC}: Preset not found: ${preset_name}"
        echo "Available presets: contract, api_spec, academic_paper, policy"
        exit 2
    fi

    # Extract YAML front matter (between --- lines)
    local front_matter
    front_matter=$(sed -n '/^---$/,/^---$/p' "$preset_file" | sed '1d;$d')

    # Extract default persona from preset if not overridden
    if [[ -z "$PERSONA" ]]; then
        PERSONA=$(echo "$front_matter" | grep 'default_persona:' | sed 's/.*default_persona:\s*//' | tr -d ' "')
    fi

    # Extract enabled strategies from preset if not overridden
    if [[ "$STRATEGIES" == "all" || -z "$STRATEGIES" ]]; then
        local enabled_strategies=""
        while IFS= read -r line; do
            local strat_name
            strat_name=$(echo "$line" | sed 's/^\s*//' | cut -d: -f1 | tr -d ' ')
            local enabled
            enabled=$(echo "$line" | grep -o 'enabled: *[a-z]*' | sed 's/enabled:\s*//' | tr -d ' ')
            if [[ "$enabled" == "true" ]]; then
                [[ -n "$enabled_strategies" ]] && enabled_strategies="${enabled_strategies},"
                enabled_strategies="${enabled_strategies}${strat_name}"
            fi
        done < <(echo "$front_matter" | sed -n '/strategies:/,/default_persona:/p' | grep -E '^\s+(contradiction|ambiguity|deletion|inversion|boundary)')
        if [[ -n "$enabled_strategies" ]]; then
            STRATEGIES="$enabled_strategies"
        fi
    fi
}

# ============================================================
# Document analysis helpers
# ============================================================

# Extract sections (headings) from markdown
extract_sections() {
    grep -nE '^#{1,4} ' "$DOCUMENT" 2>/dev/null || true
}

# Count lines and sections
document_stats() {
    local line_count section_count word_count
    line_count=$(wc -l < "$DOCUMENT")
    section_count=$(grep -cE '^#{1,4} ' "$DOCUMENT" 2>/dev/null) || section_count=0
    word_count=$(wc -w < "$DOCUMENT")
    echo "${line_count}:${section_count}:${word_count}"
}

# Get text between two section headings (by line number)
get_section_text() {
    local start_line="$1"
    local end_line="$2"
    sed -n "${start_line},${end_line}p" "$DOCUMENT"
}

# ============================================================
# Finding registration
# ============================================================
add_finding() {
    local severity="$1"
    local strategy="$2"
    local location="$3"
    local description="$4"
    local mutation="$5"
    local impact="${6:-}"
    local repair="${7:-}"

    TOTAL_MUTATIONS=$((TOTAL_MUTATIONS + 1))

    case "$severity" in
        Critical)
            KILLED_MUTATIONS=$((KILLED_MUTATIONS + 1))
            CRITICAL_COUNT=$((CRITICAL_COUNT + 1))
            ;;
        Major)
            KILLED_MUTATIONS=$((KILLED_MUTATIONS + 1))
            MAJOR_COUNT=$((MAJOR_COUNT + 1))
            ;;
        Minor)
            MINOR_COUNT=$((MINOR_COUNT + 1))
            ;;
    esac

    local finding="${severity}|${strategy}|${location}|${description}|${mutation}|${impact}|${repair}"
    FINDINGS+=("$finding")
}

# ============================================================
# Strategy S1: Contradiction
# ============================================================
run_contradiction() {
    local -a section_lines=()
    local -a section_names=()

    # Extract section headings and line numbers
    while IFS= read -r line; do
        local lnum
        lnum=$(echo "$line" | cut -d: -f1)
        local heading
        heading=$(echo "$line" | cut -d: -f2- | sed 's/^#* //')
        section_lines+=("$lnum")
        section_names+=("$heading")
    done < <(extract_sections)

    local num_sections=${#section_lines[@]}
    if [[ $num_sections -lt 2 ]]; then
        return
    fi

    # Cross-reference analysis: find sections that reference other sections
    local i j
    for ((i=0; i<num_sections; i++)); do
        local start=${section_lines[$i]}
        local end
        if [[ $((i+1)) -lt $num_sections ]]; then
            end=$((section_lines[$((i+1))] - 1))
        else
            end=$(wc -l < "$DOCUMENT")
        fi

        local section_text
        section_text=$(get_section_text "$start" "$end")

        # Check for references to other sections
        for ((j=0; j<num_sections; j++)); do
            [[ $i -eq $j ]] && continue
            local target_name="${section_names[$j]}"
            # Look for explicit references
            if echo "$section_text" | grep -qiE "section.*${target_name}|${target_name}.*section|see.*${target_name}|defined in.*${target_name}|as per.*${target_name}" 2>/dev/null; then
                TOTAL_MUTATIONS=$((TOTAL_MUTATIONS + 1))
            fi
        done

        # Check for contradictory numeric values within the document
        local numbers_in_section
        numbers_in_section=$(echo "$section_text" | grep -oE '[0-9]+\s*(days?|hours?|minutes?|percent|%|months?|years?|business days?)' 2>/dev/null || true)

        if [[ -n "$numbers_in_section" ]]; then
            while IFS= read -r numphrase; do
                local unit
                unit=$(echo "$numphrase" | grep -oE '(days?|hours?|minutes?|percent|%|months?|years?|business days?)' || true)
                [[ -z "$unit" ]] && continue

                # Check if the same unit appears elsewhere with a different value
                local other_occurrences
                other_occurrences=$(grep -n "$unit" "$DOCUMENT" 2>/dev/null | grep -v "^${start}:" || true)

                if [[ -n "$other_occurrences" ]]; then
                    local this_val
                    this_val=$(echo "$numphrase" | grep -oE '[0-9]+')
                    while IFS= read -r other_line; do
                        local other_val
                        other_val=$(echo "$other_line" | grep -oE '[0-9]+\s*'"$unit" | grep -oE '[0-9]+' | head -1)
                        if [[ -n "$other_val" && "$other_val" != "$this_val" ]]; then
                            local other_lnum
                            other_lnum=$(echo "$other_line" | cut -d: -f1)
                            add_finding "Major" "Contradiction" \
                                "Line ${start} vs Line ${other_lnum}" \
                                "Potentially conflicting values: '${this_val} ${unit}' vs '${other_val} ${unit}'" \
                                "Different numeric values for '${unit}' in separate sections" \
                                "Cross-section inconsistency" \
                                "Standardize to a single value, or add explicit exception clause"
                            break
                        fi
                    done <<< "$other_occurrences"
                fi
            done <<< "$numbers_in_section"
        fi
    done

    # Check for conflicting modal verbs (shall vs shall not for same subject)
    local shall_clauses
    shall_clauses=$(grep -n '\bshall\b' "$DOCUMENT" 2>/dev/null || true)
    local shall_not_clauses
    shall_not_clauses=$(grep -nE '\bshall not\b|\bshall never\b|\bmust not\b' "$DOCUMENT" 2>/dev/null || true)

    if [[ -n "$shall_clauses" && -n "$shall_not_clauses" ]]; then
        # Look for the same subject with both "shall" and "shall not"
        while IFS= read -r pos_line; do
            local pos_subject
            pos_subject=$(echo "$pos_line" | cut -d: -f2- | grep -oE '^\s*\S+\s+shall' | sed 's/shall//' | tr -d ' ' | tr '[:upper:]' '[:lower:]')
            [[ -z "$pos_subject" ]] && continue

            while IFS= read -r neg_line; do
                local neg_subject
                neg_subject=$(echo "$neg_line" | cut -d: -f2- | grep -oiE '^\s*\S+\s+(shall not|shall never|must not)' | sed -E 's/(shall not|shall never|must not)//' | tr -d ' ' | tr '[:upper:]' '[:lower:]')
                [[ -z "$neg_subject" ]] && continue

                if [[ "$pos_subject" == "$neg_subject" ]]; then
                    local pos_lnum neg_lnum
                    pos_lnum=$(echo "$pos_line" | cut -d: -f1)
                    neg_lnum=$(echo "$neg_line" | cut -d: -f1)
                    add_finding "Critical" "Contradiction" \
                        "Line ${pos_lnum} vs Line ${neg_lnum}" \
                        "'${pos_subject}' has both affirmative and negative obligations" \
                        "Same subject with contradictory modal verbs" \
                        "Legal/logical impossibility" \
                        "Reconcile the two clauses — determine which obligation takes precedence"
                fi
            done <<< "$shall_not_clauses"
        done <<< "$shall_clauses"
    fi
}

# ============================================================
# Strategy S2: Ambiguity
# ============================================================
run_ambiguity() {
    for modifier in "${VAGUE_MODIFIERS[@]}"; do
        local matches
        matches=$(grep -niE "\b${modifier}\b" "$DOCUMENT" 2>/dev/null || true)

        if [[ -n "$matches" ]]; then
            while IFS= read -r match_line; do
                local lnum
                lnum=$(echo "$match_line" | cut -d: -f1)
                local line_text
                line_text=$(echo "$match_line" | cut -d: -f2-)

                # Determine severity based on context
                local severity="Minor"
                if echo "$line_text" | grep -qiE 'shall|must|obligat|required|entitled|rights?|deadline|within.*days' 2>/dev/null; then
                    severity="Critical"
                elif echo "$line_text" | grep -qiE 'scope|defin|means|includ|condition|criteria' 2>/dev/null; then
                    severity="Major"
                fi

                # Determine repair suggestion
                local repair_text=""
                if [[ "$REPAIR" == true ]]; then
                    repair_text="Replace '${modifier}' with a specific, measurable term"
                fi

                add_finding "$severity" "Ambiguity" \
                    "Line ${lnum}" \
                    "Vague modifier '${modifier}' — meaning is undefined and open to interpretation" \
                    "'${modifier}' → extreme test: replace with 'zero' or 'unlimited'" \
                    "Ambiguous language in $(echo "$severity" | tr '[:upper:]' '[:lower:]') context" \
                    "$repair_text"
            done <<< "$matches"
        fi
    done
}

# ============================================================
# Strategy S3: Deletion
# ============================================================
run_deletion() {
    local -a section_lines=()
    local -a section_names=()
    local -a section_levels=()

    while IFS= read -r line; do
        local lnum
        lnum=$(echo "$line" | cut -d: -f1)
        local heading
        heading=$(echo "$line" | cut -d: -f2-)
        local level
        level=$(echo "$heading" | grep -oE '^#{1,4}' | wc -c)
        level=$((level - 1))
        heading=$(echo "$heading" | sed 's/^#* //')
        section_lines+=("$lnum")
        section_names+=("$heading")
        section_levels+=("$level")
    done < <(extract_sections)

    local num_sections=${#section_lines[@]}
    [[ $num_sections -lt 2 ]] && return

    local total_lines
    total_lines=$(wc -l < "$DOCUMENT")

    for ((i=0; i<num_sections; i++)); do
        local name="${section_names[$i]}"
        local start=${section_lines[$i]}
        local end
        if [[ $((i+1)) -lt $num_sections ]]; then
            end=$((section_lines[$((i+1))] - 1))
        else
            end=$total_lines
        fi

        local section_size=$((end - start + 1))

        # Count references to this section from OTHER sections
        local ref_count=0
        local name_escaped
        name_escaped=$(echo "$name" | sed 's/[.[\*^$()+?{|]/\\&/g')

        # Count how many times this section name is mentioned outside its own section
        local before_refs=0
        local after_refs=0
        if [[ $start -gt 1 ]]; then
            before_refs=$(sed -n "1,$((start-1))p" "$DOCUMENT" | grep -ciE "$name_escaped" 2>/dev/null) || before_refs=0
        fi
        if [[ $end -lt $total_lines ]]; then
            after_refs=$(sed -n "$((end+1)),${total_lines}p" "$DOCUMENT" | grep -ciE "$name_escaped" 2>/dev/null) || after_refs=0
        fi
        ref_count=$((before_refs + after_refs))

        TOTAL_MUTATIONS=$((TOTAL_MUTATIONS + 1))

        if [[ $ref_count -eq 0 ]]; then
            # Dead clause — zero references from other sections
            DEAD_CLAUSE_COUNT=$((DEAD_CLAUSE_COUNT + 1))
            KILLED_MUTATIONS=$((KILLED_MUTATIONS + 1))

            add_finding "Minor" "Deletion" \
                "Line ${start}: '${name}'" \
                "Dead clause — no other section references this section (impact score: 0)" \
                "Remove section '${name}' and observe: nothing else changes" \
                "Zero structural impact" \
                "Consider removing this section or documenting why it exists independently"
        elif [[ $ref_count -ge 3 ]]; then
            # Critical dependency — many references
            add_finding "Major" "Deletion" \
                "Line ${start}: '${name}'" \
                "Critical dependency — ${ref_count} other sections reference this section" \
                "Remove section '${name}': ${ref_count} sections would lose a dependency" \
                "High structural impact (referenced ${ref_count} times)" \
                "Ensure this section is carefully maintained; errors cascade broadly"
        fi
    done
}

# ============================================================
# Strategy S4: Inversion
# ============================================================
run_inversion() {
    for indicator in "${CLAIM_INDICATORS[@]}"; do
        local matches
        matches=$(grep -niE "\b${indicator}\b" "$DOCUMENT" 2>/dev/null || true)
        [[ -z "$matches" ]] && continue

        while IFS= read -r match_line; do
            local lnum
            lnum=$(echo "$match_line" | cut -d: -f1)
            local line_text
            line_text=$(echo "$match_line" | cut -d: -f2-)

            TOTAL_MUTATIONS=$((TOTAL_MUTATIONS + 1))

            # Check if there's supporting evidence/justification nearby
            local context_start=$((lnum > 3 ? lnum - 3 : 1))
            local context_end=$((lnum + 3))
            local context
            context=$(sed -n "${context_start},${context_end}p" "$DOCUMENT")

            local has_evidence=false
            if echo "$context" | grep -qiE 'because|therefore|evidence|data shows|according to|based on|proven|demonstrated|research|study|analysis' 2>/dev/null; then
                has_evidence=true
            fi

            if [[ "$has_evidence" == false ]]; then
                # Unsupported claim — vulnerable to inversion
                local severity="Major"
                if echo "$line_text" | grep -qiE 'shall|must|certif|warrant|guarant' 2>/dev/null; then
                    severity="Critical"
                fi

                add_finding "$severity" "Inversion" \
                    "Line ${lnum}" \
                    "Claim '${indicator}...' has no supporting evidence within context — vulnerable to inversion" \
                    "Invert: if the opposite were true, does the document still hold?" \
                    "Unsupported assertion" \
                    "Add supporting evidence, or qualify the claim with conditions"
            fi
        done <<< "$matches"
    done
}

# ============================================================
# Strategy S5: Boundary
# ============================================================
run_boundary() {
    # Find all numeric parameters in the document
    local numeric_matches
    numeric_matches=$(grep -nE '[0-9]+(\.[0-9]+)?\s*(days?|hours?|minutes?|seconds?|percent|%|USD|\$|EUR|€|months?|years?|weeks?|business days?|times?|attempts?|retries)' "$DOCUMENT" 2>/dev/null || true)

    if [[ -z "$numeric_matches" ]]; then
        return
    fi

    while IFS= read -r match_line; do
        local lnum
        lnum=$(echo "$match_line" | cut -d: -f1)
        local line_text
        line_text=$(echo "$match_line" | cut -d: -f2-)

        # Extract the numeric value and unit
        local num_with_unit
        num_with_unit=$(echo "$line_text" | grep -oE '[0-9]+(\.[0-9]+)?\s*(days?|hours?|minutes?|seconds?|percent|%|USD|\$|EUR|€|months?|years?|weeks?|business days?|times?|attempts?|retries)' | head -1)
        [[ -z "$num_with_unit" ]] && continue

        local num_val
        num_val=$(echo "$num_with_unit" | grep -oE '[0-9]+(\.[0-9]+)?' | head -1)
        local unit
        unit=$(echo "$num_with_unit" | grep -oE '[a-zA-Z%$€]+.*' | head -1)

        TOTAL_MUTATIONS=$((TOTAL_MUTATIONS + 1))

        # Test boundary: what if value is 10x or 0.1x?
        local val_10x val_01x
        val_10x=$(echo "$num_val * 10" | bc 2>/dev/null || echo "$((num_val * 10))")
        val_01x=$(echo "scale=1; $num_val / 10" | bc 2>/dev/null || echo "0")

        # Determine severity based on what the number controls
        local severity="Minor"
        if echo "$line_text" | grep -qiE 'shall|must|obligat|required|SLA|uptime|deadline|penalty|liability|cap|limit|maximum|minimum' 2>/dev/null; then
            severity="Critical"
        elif echo "$line_text" | grep -qiE 'should|recommend|target|goal|expect|estimate' 2>/dev/null; then
            severity="Major"
        fi

        add_finding "$severity" "Boundary" \
            "Line ${lnum}" \
            "Numeric parameter '${num_val} ${unit}' — is this value justified?" \
            "Boundary test: 10x=${val_10x} ${unit}, 0.1x=${val_01x} ${unit}. Does the document still make sense?" \
            "Parameter sensitivity — how robust is the document if this number changes?" \
            "Document the rationale for choosing '${num_val}', or define acceptable range"
    done <<< "$numeric_matches"
}

# ============================================================
# Persona filtering
# ============================================================
apply_persona() {
    local persona_name="$1"

    case "$persona_name" in
        opposing_counsel)
            # Elevate ambiguity and contradiction findings in obligation context
            local i
            for ((i=0; i<${#FINDINGS[@]}; i++)); do
                local finding="${FINDINGS[$i]}"
                local strategy
                strategy=$(echo "$finding" | cut -d'|' -f2)
                local desc
                desc=$(echo "$finding" | cut -d'|' -f4)

                if [[ "$strategy" == "Ambiguity" || "$strategy" == "Contradiction" ]]; then
                    local current_severity
                    current_severity=$(echo "$finding" | cut -d'|' -f1)
                    if [[ "$current_severity" == "Minor" ]]; then
                        FINDINGS[$i]="Major|${finding#*|}"
                        MINOR_COUNT=$((MINOR_COUNT - 1))
                        MAJOR_COUNT=$((MAJOR_COUNT + 1))
                        KILLED_MUTATIONS=$((KILLED_MUTATIONS + 1))
                    fi
                fi
            done
            ;;
        naive_implementer)
            # Elevate ambiguity and boundary findings (implementer takes things literally)
            local i
            for ((i=0; i<${#FINDINGS[@]}; i++)); do
                local finding="${FINDINGS[$i]}"
                local strategy
                strategy=$(echo "$finding" | cut -d'|' -f2)

                if [[ "$strategy" == "Ambiguity" || "$strategy" == "Boundary" ]]; then
                    local current_severity
                    current_severity=$(echo "$finding" | cut -d'|' -f1)
                    if [[ "$current_severity" == "Minor" ]]; then
                        FINDINGS[$i]="Major|${finding#*|}"
                        MINOR_COUNT=$((MINOR_COUNT - 1))
                        MAJOR_COUNT=$((MAJOR_COUNT + 1))
                        KILLED_MUTATIONS=$((KILLED_MUTATIONS + 1))
                    fi
                fi
            done
            ;;
        adversarial_reader)
            # Elevate inversion findings (adversarial reader challenges all claims)
            local i
            for ((i=0; i<${#FINDINGS[@]}; i++)); do
                local finding="${FINDINGS[$i]}"
                local strategy
                strategy=$(echo "$finding" | cut -d'|' -f2)

                if [[ "$strategy" == "Inversion" ]]; then
                    local current_severity
                    current_severity=$(echo "$finding" | cut -d'|' -f1)
                    if [[ "$current_severity" == "Minor" ]]; then
                        FINDINGS[$i]="Major|${finding#*|}"
                        MINOR_COUNT=$((MINOR_COUNT - 1))
                        MAJOR_COUNT=$((MAJOR_COUNT + 1))
                        KILLED_MUTATIONS=$((KILLED_MUTATIONS + 1))
                    fi
                fi
            done
            ;;
    esac
}

# ============================================================
# Report generation
# ============================================================
generate_report_markdown() {
    local filename
    filename=$(basename "$DOCUMENT")
    local kill_score=0
    if [[ $TOTAL_MUTATIONS -gt 0 ]]; then
        kill_score=$((KILLED_MUTATIONS * 100 / TOTAL_MUTATIONS))
    fi
    local date_str
    date_str=$(date +%Y-%m-%d)

    local preset_display="${PRESET:-auto}"
    local persona_display="${PERSONA:-none}"

    cat <<EOF
# MutaDoc Report: ${filename}

> Preset: ${preset_display} | Persona: ${persona_display}
> Mutation Kill Score: ${kill_score}% (${KILLED_MUTATIONS} killed / ${TOTAL_MUTATIONS} applied)
> Generated: ${date_str}

## Summary
- Critical: ${CRITICAL_COUNT}
- Major: ${MAJOR_COUNT}
- Minor: ${MINOR_COUNT}
- Dead Clauses: ${DEAD_CLAUSE_COUNT}

EOF

    # Group findings by severity
    local finding_num=0

    if [[ $CRITICAL_COUNT -gt 0 ]]; then
        echo "## Critical Findings"
        echo ""
        local crit_num=0
        for finding in "${FINDINGS[@]}"; do
            local severity
            severity=$(echo "$finding" | cut -d'|' -f1)
            [[ "$severity" != "Critical" ]] && continue
            crit_num=$((crit_num + 1))

            local strategy location desc mutation impact repair
            strategy=$(echo "$finding" | cut -d'|' -f2)
            location=$(echo "$finding" | cut -d'|' -f3)
            desc=$(echo "$finding" | cut -d'|' -f4)
            mutation=$(echo "$finding" | cut -d'|' -f5)
            impact=$(echo "$finding" | cut -d'|' -f6)
            repair=$(echo "$finding" | cut -d'|' -f7)

            echo "### [C${crit_num}] ${strategy}: ${desc}"
            echo "- **Location**: ${location}"
            echo "- **Strategy**: ${strategy}"
            echo "- **Mutation**: ${mutation}"
            echo "- **Impact**: ${impact}"
            if [[ -n "$repair" && "$REPAIR" == true ]]; then
                echo "- **Repair Suggestion**: ${repair}"
            fi
            echo ""
        done
    fi

    if [[ $MAJOR_COUNT -gt 0 ]]; then
        echo "## Major Findings"
        echo ""
        local maj_num=0
        for finding in "${FINDINGS[@]}"; do
            local severity
            severity=$(echo "$finding" | cut -d'|' -f1)
            [[ "$severity" != "Major" ]] && continue
            maj_num=$((maj_num + 1))

            local strategy location desc mutation impact repair
            strategy=$(echo "$finding" | cut -d'|' -f2)
            location=$(echo "$finding" | cut -d'|' -f3)
            desc=$(echo "$finding" | cut -d'|' -f4)
            mutation=$(echo "$finding" | cut -d'|' -f5)
            impact=$(echo "$finding" | cut -d'|' -f6)
            repair=$(echo "$finding" | cut -d'|' -f7)

            echo "### [M${maj_num}] ${strategy}: ${desc}"
            echo "- **Location**: ${location}"
            echo "- **Strategy**: ${strategy}"
            echo "- **Mutation**: ${mutation}"
            echo "- **Impact**: ${impact}"
            if [[ -n "$repair" && "$REPAIR" == true ]]; then
                echo "- **Repair Suggestion**: ${repair}"
            fi
            echo ""
        done
    fi

    if [[ $MINOR_COUNT -gt 0 ]]; then
        echo "## Minor Findings"
        echo ""
        local min_num=0
        for finding in "${FINDINGS[@]}"; do
            local severity
            severity=$(echo "$finding" | cut -d'|' -f1)
            [[ "$severity" != "Minor" ]] && continue
            min_num=$((min_num + 1))

            local strategy location desc mutation
            strategy=$(echo "$finding" | cut -d'|' -f2)
            location=$(echo "$finding" | cut -d'|' -f3)
            desc=$(echo "$finding" | cut -d'|' -f4)
            mutation=$(echo "$finding" | cut -d'|' -f5)

            echo "### [m${min_num}] ${strategy}: ${desc}"
            echo "- **Location**: ${location}"
            echo "- **Mutation**: ${mutation}"
            echo ""
        done
    fi

    if [[ $CRITICAL_COUNT -eq 0 && $MAJOR_COUNT -eq 0 && $MINOR_COUNT -eq 0 ]]; then
        echo "## No Findings"
        echo ""
        echo "All mutation tests passed. No vulnerabilities detected."
        echo ""
    fi
}

generate_report_text() {
    local filename
    filename=$(basename "$DOCUMENT")
    local kill_score=0
    if [[ $TOTAL_MUTATIONS -gt 0 ]]; then
        kill_score=$((KILLED_MUTATIONS * 100 / TOTAL_MUTATIONS))
    fi

    echo -e "${BOLD}MutaDoc Report: ${filename}${NC}"
    echo -e "Preset: ${PRESET:-auto} | Persona: ${PERSONA:-none}"
    echo -e "Mutation Kill Score: ${BOLD}${kill_score}%${NC} (${KILLED_MUTATIONS}/${TOTAL_MUTATIONS})"
    echo ""

    # Summary with colors
    echo -e "  ${RED}Critical${NC}: ${CRITICAL_COUNT}"
    echo -e "  ${YELLOW}Major${NC}:    ${MAJOR_COUNT}"
    echo -e "  ${GRAY}Minor${NC}:    ${MINOR_COUNT}"
    echo -e "  Dead Clauses: ${DEAD_CLAUSE_COUNT}"
    echo ""

    if [[ ${#FINDINGS[@]} -eq 0 ]]; then
        echo -e "  ${GREEN}✓ All mutation tests passed.${NC}"
        return
    fi

    # Print findings with colors
    for finding in "${FINDINGS[@]}"; do
        local severity strategy location desc mutation impact repair
        severity=$(echo "$finding" | cut -d'|' -f1)
        strategy=$(echo "$finding" | cut -d'|' -f2)
        location=$(echo "$finding" | cut -d'|' -f3)
        desc=$(echo "$finding" | cut -d'|' -f4)
        mutation=$(echo "$finding" | cut -d'|' -f5)
        impact=$(echo "$finding" | cut -d'|' -f6)
        repair=$(echo "$finding" | cut -d'|' -f7)

        local color="$GRAY"
        case "$severity" in
            Critical) color="$RED" ;;
            Major) color="$YELLOW" ;;
        esac

        echo -e "  ${color}${severity}${NC} ${BOLD}${strategy}${NC}: ${location}"
        echo -e "    ${desc}"
        echo -e "    ${GRAY}Mutation: ${mutation}${NC}"
        if [[ -n "$repair" && "$REPAIR" == true ]]; then
            echo -e "    ${CYAN}Repair: ${repair}${NC}"
        fi
        echo ""
    done
}

generate_report_json() {
    local filename
    filename=$(basename "$DOCUMENT")
    local kill_score=0
    if [[ $TOTAL_MUTATIONS -gt 0 ]]; then
        kill_score=$((KILLED_MUTATIONS * 100 / TOTAL_MUTATIONS))
    fi
    local date_str
    date_str=$(date +%Y-%m-%dT%H:%M:%S%z)

    echo "{"
    echo "  \"metadata\": {"
    echo "    \"document\": \"${filename}\","
    echo "    \"preset\": \"${PRESET:-auto}\","
    echo "    \"persona\": \"${PERSONA:-none}\","
    echo "    \"version\": \"${VERSION}\","
    echo "    \"timestamp\": \"${date_str}\""
    echo "  },"
    echo "  \"score\": {"
    echo "    \"kill_score\": ${kill_score},"
    echo "    \"killed\": ${KILLED_MUTATIONS},"
    echo "    \"total\": ${TOTAL_MUTATIONS}"
    echo "  },"
    echo "  \"summary\": {"
    echo "    \"critical\": ${CRITICAL_COUNT},"
    echo "    \"major\": ${MAJOR_COUNT},"
    echo "    \"minor\": ${MINOR_COUNT},"
    echo "    \"dead_clauses\": ${DEAD_CLAUSE_COUNT}"
    echo "  },"
    echo "  \"findings\": ["

    local first=true
    for finding in "${FINDINGS[@]}"; do
        local severity strategy location desc mutation impact repair
        severity=$(echo "$finding" | cut -d'|' -f1)
        strategy=$(echo "$finding" | cut -d'|' -f2)
        location=$(echo "$finding" | cut -d'|' -f3)
        desc=$(echo "$finding" | cut -d'|' -f4)
        mutation=$(echo "$finding" | cut -d'|' -f5)
        impact=$(echo "$finding" | cut -d'|' -f6)
        repair=$(echo "$finding" | cut -d'|' -f7)

        # Escape double quotes in strings
        desc=$(echo "$desc" | sed 's/"/\\"/g')
        mutation=$(echo "$mutation" | sed 's/"/\\"/g')
        impact=$(echo "$impact" | sed 's/"/\\"/g')
        repair=$(echo "$repair" | sed 's/"/\\"/g')

        if [[ "$first" == true ]]; then
            first=false
        else
            echo "    ,"
        fi

        echo "    {"
        echo "      \"severity\": \"${severity}\","
        echo "      \"strategy\": \"${strategy}\","
        echo "      \"location\": \"${location}\","
        echo "      \"description\": \"${desc}\","
        echo "      \"mutation\": \"${mutation}\","
        echo "      \"impact\": \"${impact}\","
        echo "      \"repair\": \"${repair}\""
        echo "    }"
    done

    echo "  ]"
    echo "}"
}

generate_score_output() {
    local filename
    filename=$(basename "$DOCUMENT")
    local kill_score=0
    if [[ $TOTAL_MUTATIONS -gt 0 ]]; then
        kill_score=$((KILLED_MUTATIONS * 100 / TOTAL_MUTATIONS))
    fi

    if [[ "$FORMAT" == "json" ]]; then
        echo "{\"document\":\"${filename}\",\"kill_score\":${kill_score},\"killed\":${KILLED_MUTATIONS},\"total\":${TOTAL_MUTATIONS}}"
    else
        echo -e "${BOLD}${filename}${NC}: Mutation Kill Score ${BOLD}${kill_score}%${NC} (${KILLED_MUTATIONS}/${TOTAL_MUTATIONS})"
        if [[ $CRITICAL_COUNT -gt 0 ]]; then
            echo -e "  ${RED}${CRITICAL_COUNT} Critical${NC}, ${YELLOW}${MAJOR_COUNT} Major${NC}"
        elif [[ $MAJOR_COUNT -gt 0 ]]; then
            echo -e "  ${YELLOW}${MAJOR_COUNT} Major${NC}"
        else
            echo -e "  ${GREEN}✓ Pass${NC}"
        fi
    fi
}

# ============================================================
# Strategy dispatcher
# ============================================================
run_strategies() {
    local strategy_list="$1"

    if [[ "$strategy_list" == "all" ]]; then
        strategy_list="contradiction,ambiguity,deletion,inversion,boundary"
    fi

    IFS=',' read -ra strats <<< "$strategy_list"
    for strat in "${strats[@]}"; do
        strat=$(echo "$strat" | tr -d ' ')
        case "$strat" in
            contradiction) run_contradiction ;;
            ambiguity)     run_ambiguity ;;
            deletion)      run_deletion ;;
            inversion)     run_inversion ;;
            boundary)      run_boundary ;;
            *)
                echo -e "${YELLOW}Warning${NC}: Unknown strategy '${strat}', skipping."
                ;;
        esac
    done
}

# ============================================================
# Main
# ============================================================
main() {
    parse_args "$@"

    # Load preset if specified
    if [[ -n "$PRESET" ]]; then
        load_preset "$PRESET"
    fi

    # Progress indicator
    if [[ "$FORMAT" != "json" && "$SUBCMD" != "score" ]]; then
        local filename
        filename=$(basename "$DOCUMENT")
        local stats
        stats=$(document_stats)
        local lines sections words
        lines=$(echo "$stats" | cut -d: -f1)
        sections=$(echo "$stats" | cut -d: -f2)
        words=$(echo "$stats" | cut -d: -f3)

        echo -e "${BOLD}mutadoc${NC} v${VERSION} — Mutation Testing for Documents"
        echo -e "Target: ${CYAN}${filename}${NC} (${lines} lines, ${sections} sections, ${words} words)"
        if [[ -n "$PRESET" ]]; then
            echo -e "Preset: ${CYAN}${PRESET}${NC}"
        fi
        if [[ -n "$PERSONA" ]]; then
            echo -e "Persona: ${CYAN}${PERSONA}${NC}"
        fi
        echo -e "Strategies: ${CYAN}${STRATEGIES}${NC}"
        echo ""
    fi

    # Run strategies
    run_strategies "$STRATEGIES"

    # Apply persona filter
    if [[ -n "$PERSONA" ]]; then
        apply_persona "$PERSONA"
    fi

    # Generate output
    local report=""
    case "$SUBCMD" in
        score)
            report=$(generate_score_output)
            ;;
        test|quick)
            case "$FORMAT" in
                markdown) report=$(generate_report_markdown) ;;
                text)     report=$(generate_report_text) ;;
                json)     report=$(generate_report_json) ;;
                *)
                    echo -e "${RED}Error${NC}: Unknown format '${FORMAT}'. Use markdown, text, or json."
                    exit 2
                    ;;
            esac
            ;;
    esac

    # Output
    if [[ -n "$OUTPUT" ]]; then
        echo "$report" > "$OUTPUT"
        if [[ "$FORMAT" != "json" ]]; then
            echo -e "${GREEN}Report written to${NC}: ${OUTPUT}"
        fi
    else
        echo "$report"
    fi

    # Exit code
    if [[ $CRITICAL_COUNT -gt 0 || $MAJOR_COUNT -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

main "$@"
