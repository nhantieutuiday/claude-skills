---
name: js-logic-analyst
description: Analyze frontend JavaScript behavior and business logic for authorized bug bounty testing. Use when Codex needs to reason about hidden functions, role checks, feature gates, client-side validation, workflow transitions, object ownership, API wrappers, payment or billing logic, invite/team logic, admin paths, and likely vulnerability paths from JS evidence.
---

# JS Logic Analyst

## Analysis Rules

Treat frontend checks as signals, not proof of server weakness. Convert each signal into a server-side validation question, exploit path, and safe test plan.

Track data flow from UI action to request construction to response handling. Prioritize actions that mutate state, cross tenant/user boundaries, or affect money, roles, access, data export, or compliance workflows.

## Exploit Reasoning Rules

When JS shows a bug-like signal, automatically infer how it could be exploited if the server-side control is missing. Keep this as a hypothesis until validated.

For each candidate, derive:

- Actor: anonymous, normal user, lower-tier user, member, admin, partner, cross-tenant user.
- Target object: user, account, tenant, workspace, invoice, invite, role, export, file, webhook, subscription, workflow item.
- Bypass primitive: replay hidden request, edit object ID, edit tenant ID, change role/status/plan/price field, call admin route directly, skip UI validation, alter redirect/webhook URL, repeat GraphQL mutation.
- Missing server control: authorization, tenant isolation, role enforcement, workflow state enforcement, server-side price recompute, allowlist, file validation, rate limit, CSRF/CORS control.
- Vulnerable signal: 200/2xx, data from another object, state changed despite UI rule, accepted forbidden field, redirect to untrusted URL, callback fired, export generated, role/plan changed.
- Safe test shape: placeholder request or browser steps using user-owned objects and reversible changes.

## Workflow

1. Identify the feature boundary.
   - Name the feature, user role, object type, tenant/project boundary, and expected business rule.

2. Trace request construction.
   - Find API client wrappers, route constants, GraphQL operations, fetch/axios calls, headers, CSRF handling, object IDs, and body serialization.

3. Locate client-side decisions.
   - Record permission checks, feature flags, disabled buttons, pricing/plan checks, validation regexes, workflow status checks, and environment checks.

4. Convert signals to server questions.
   - Example: `if (!isAdmin) hideDeleteButton` becomes "Does the delete endpoint enforce admin server-side?"
   - Example: `plan === enterprise` becomes "Can lower-tier users call the enterprise endpoint directly?"

5. Build exploit path.
   - Chain the evidence into `actor -> precondition -> request manipulation -> missing server control -> vulnerable signal -> impact`.
   - Mark the path `Ready`, `Needs test`, or `Weak` based on evidence quality.
   - Avoid operational exploit detail when the path would affect other users, real money, production integrity, or third-party infrastructure; provide a safe validation plan instead.

6. Design minimal validation.
   - Suggest low-impact requests using the user's own account or authorized test accounts.
   - Avoid destructive actions unless the program allows them and the request can be made reversible.

7. Rank likely issues.
   - Rank by authorization boundary, object ownership, state change, business impact, reproducibility, and evidence quality.

## Output Format

```markdown
## Feature Boundary
- Feature:
- Roles / tenants:
- Business rule:

## Evidence Trace
| Code signal | Request/route | Client decision | Server-side question | Exploit cue |

## Exploit Paths
| Rank | Status | Actor | Chain | Missing server control | Vulnerable signal | Safe validation |

## Candidate Vulnerabilities
| Rank | Hypothesis | Evidence | Minimal test | Impact if confirmed |

## False Positive Checks
- Expected server controls:
- Missing evidence:
```

## References

Read [references/business-logic-patterns.md](references/business-logic-patterns.md) when mapping JS behavior to vulnerability classes.
