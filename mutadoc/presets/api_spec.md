---
preset:
  name: api_spec
  description: "API and technical specifications (OpenAPI, gRPC, REST)"
  strategies:
    contradiction: { weight: 1.0, enabled: true }
    ambiguity: { weight: 0.7, enabled: true }
    deletion: { weight: 0.8, enabled: true }
    inversion: { weight: 0.6, enabled: true }
    boundary: { weight: 1.0, enabled: true }
  default_persona: naive_implementer
  severity_overrides:
    undefined_boundary: Critical
    contradictory_schema: Critical
    missing_error_code: Major
    ambiguous_auth_scope: Critical
    undocumented_side_effect: Major
  domain_terminology:
    - endpoint
    - schema
    - authentication
    - rate limit
    - idempotent
    - pagination
    - webhook
    - payload
    - status code
    - content type
    - CORS
    - OAuth
    - bearer token
    - request body
    - query parameter
  output_format: full_report
---

# Preset: API Specification

Mutation testing configuration for API and technical specifications. Designed to find inconsistencies, undefined boundaries, and ambiguities that would cause implementation bugs, security vulnerabilities, or integration failures.

## Target Document Types

- **OpenAPI/Swagger specifications**: REST API definitions in YAML or JSON
- **gRPC/Protobuf specifications**: Service and message definitions
- **GraphQL schemas**: Type definitions and query specifications
- **API documentation**: Markdown/HTML API reference documents
- **Technical design documents**: System architecture and interface specifications

## Strategy Configuration

### Contradiction (weight: 1.0)

Highest priority alongside Boundary. API specifications with contradictions cause implementation bugs that are expensive to discover at integration time.

**What it does**: Identifies inconsistencies between different parts of the specification.

**API-specific mutations**:
- Swap request/response schemas between endpoints to test if type constraints are explicit
- Change HTTP method semantics (GET with body, DELETE returning created resource) to test if method documentation is complete
- Contradict authentication requirements between overview section and individual endpoints

### Boundary (weight: 1.0)

Co-highest priority. APIs without defined boundaries create security vulnerabilities (unbounded queries), performance issues (no pagination limits), and reliability failures (no timeout specs).

**What it does**: Pushes numeric values, sizes, and rates to extremes to find undefined limits.

**API-specific mutations**:
- "rate limit: 100/min" → "rate limit: 0/min" (does the spec define behavior at zero?)
- "max payload: 10MB" → "max payload: 10TB" (is there an upper bound?)
- Pagination: "page_size=100" → "page_size=0" or "page_size=999999"
- "timeout: 30s" → "timeout: 0s" (does the spec define instant-timeout behavior?)
- Array fields: test with empty array, single element, and 10,000 elements

### Deletion (weight: 0.8)

High priority. Tests whether each endpoint, field, and parameter is structurally necessary and properly cross-referenced.

**What it does**: Removes individual endpoints, fields, or parameters and measures cascading impact.

**API-specific mutations**:
- Delete a required field from a request schema — does any error handling spec cover this?
- Delete an entire endpoint — do other endpoints reference it (e.g., "create" used by "batch create")?
- Remove an error code from the error table — is it referenced in endpoint documentation?
- Delete authentication section — do individual endpoints specify auth independently?

### Ambiguity (weight: 0.7)

Above moderate priority. Technical specifications should be precise, but natural language descriptions often introduce ambiguity.

**What it does**: Identifies terms and descriptions that could be interpreted differently by different implementers.

**API-specific mutations**:
- Replace "should" with "must" or "may" to test if RFC 2119 language is consistent
- Replace "a list of items" with "an ordered list" or "an unordered set" to test collection semantics
- Test whether "string" fields have format constraints (email? URL? UUID? freeform?)
- Replace "recent" with "last 24 hours" or "last 7 days" to reveal undefined temporal terms

### Inversion (weight: 0.6)

Moderate priority. Tests the robustness of API behavior by reversing expected patterns.

**What it does**: Reverses documented behaviors to identify implicit assumptions.

**API-specific mutations**:
- "returns 200 OK" → "returns 500 Internal Server Error" — does the client error handling cover this?
- "required: true" → "required: false" — does the endpoint's logic handle missing optional fields?
- "ascending order" → "descending order" — is sort order documented or assumed?

## Default Persona Rationale

**Naive Implementer** (`naive_implementer`) is the default persona because:

1. The most common API bugs come from implementers who follow the spec literally without understanding intent
2. A naive implementer reveals every gap between "what the spec says" and "what it means"
3. Edge cases that "obviously" should work a certain way are exactly the ones that break when implemented literally
4. This persona exposes missing error handling, undefined defaults, and implicit assumptions

Alternative personas for specific use cases:
- `adversarial_reader`: For security-focused API review (finding exploitable gaps)
- `opposing_counsel`: For API contracts/SLAs where legal precision matters

## Severity Overrides Explanation

| Override | Default → Override | Rationale |
|----------|-------------------|-----------|
| `undefined_boundary` | Major → **Critical** | APIs without defined limits are vulnerable to DoS, resource exhaustion, and unbounded costs. Every numeric parameter needs min/max. |
| `contradictory_schema` | Major → **Critical** | Schema contradictions (field is "string" in request but "integer" in response) cause serialization failures at runtime. |
| `missing_error_code` | Minor → **Major** | Undocumented error codes force implementers to guess error handling, leading to silent failures or crashes. |
| `ambiguous_auth_scope` | Major → **Critical** | Ambiguous authentication requirements are security vulnerabilities. If it's unclear whether an endpoint requires auth, someone will deploy it without auth. |
| `undocumented_side_effect` | Minor → **Major** | An endpoint that silently modifies state beyond its documented scope causes data corruption in integrations. |

## Domain Terminology

| Term | Spec Meaning | Implementation Implication |
|------|-------------|---------------------------|
| **Endpoint** | A specific URL path + HTTP method combination | Each endpoint needs independent documentation of auth, params, and responses |
| **Schema** | Structured definition of request/response data shapes | Must define type, required/optional, format, and constraints for every field |
| **Idempotent** | Multiple identical requests produce the same result | PUT and DELETE should be idempotent; POST typically is not |
| **Rate limit** | Maximum requests per time window | Must define: window size, limit count, response when exceeded, reset behavior |
| **Pagination** | Splitting large result sets into pages | Must define: page size limits, cursor/offset semantics, total count availability |
| **Status code** | HTTP response code indicating result type | Each endpoint should document all possible status codes, not just 200 |
| **CORS** | Cross-Origin Resource Sharing headers | Must document allowed origins, methods, and headers for browser-based clients |

## Usage Examples

```bash
# Test an OpenAPI specification
mutadoc test openapi.yaml --preset api_spec

# Focus on boundary testing for a payments API
mutadoc test payments_api.md --preset api_spec --strategies boundary

# Test with adversarial reader for security review
mutadoc test auth_api.yaml --preset api_spec --persona adversarial_reader

# Output as CI gate format (pass/fail only)
mutadoc test api_spec.yaml --preset api_spec --format ci_gate

# Test only Critical and Major findings
mutadoc test graphql_schema.md --preset api_spec --min-severity major
```

## Sample Output

```markdown
# MutaDoc Report: payments_api.yaml
**Preset**: api_spec | **Persona**: naive_implementer | **Score**: 65/100

## Critical Findings (3)

### [C-001] Undefined Rate Limit Boundary (Boundary)
- **Location**: POST /payments — Rate Limiting section
- **Finding**: Rate limit is documented as "100 requests per minute" but does not define:
  (a) behavior when limit is exceeded (429? 503? silent drop?),
  (b) whether the limit is per-API-key or per-IP,
  (c) whether the minute window is rolling or fixed.
- **Implementation Risk**: Without (a), a naive implementer will not handle rate limiting at
  all. Without (b), shared infrastructure will hit limits unexpectedly. Without (c), burst
  traffic patterns will behave inconsistently.
- **Recommendation**: Add: "Returns 429 Too Many Requests with Retry-After header. Limit is
  per API key. Window is rolling 60 seconds."

### [C-002] Contradictory Amount Schema (Contradiction)
- **Location**: POST /payments (request) vs GET /payments/{id} (response)
- **Finding**: Request body defines `amount` as `type: integer` (cents) but response defines
  `amount` as `type: string` with format "decimal" (e.g., "49.99"). The same field name
  represents different types in different contexts.
- **Implementation Risk**: A naive implementer sending `4999` (integer cents) will receive
  "49.99" (string dollars) and will either crash on type mismatch or silently misinterpret
  the value by a factor of 100.
- **Recommendation**: Use consistent representation. Prefer integer cents with explicit
  `currency` field, or string decimals everywhere with documented precision.

### [C-003] Ambiguous Authentication Scope (Ambiguity)
- **Location**: Security section vs POST /payments/refund
- **Finding**: The global security section states "All endpoints require Bearer token
  authentication" but POST /payments/refund has no security requirement listed. Is it
  intentionally public or accidentally undocumented?
- **Implementation Risk**: If a naive implementer follows the endpoint-level spec (no auth),
  the refund endpoint is publicly accessible — a critical security vulnerability.
- **Recommendation**: Explicitly state security requirements on every endpoint, even if
  repeating the global default.

## Major Findings (4)

### [M-001] Missing Error Code (Deletion)
- **Location**: POST /payments — Error Responses
- **Finding**: Error table lists 400, 401, 403, and 500 but not 402 (Payment Required) or
  422 (Unprocessable Entity). For a payments API, these are the most likely error scenarios.
- **Impact**: Implementers will not handle payment-specific failures gracefully.

...

## Summary
| Severity | Count |
|----------|-------|
| Critical | 3 |
| Major | 4 |
| Minor | 6 |
| **Total Mutations Applied** | **31** |
| **Mutations Survived (undetected)** | **11** |
| **Mutation Kill Rate** | **65%** |
```
