---
name: vuln-triage-reasoner
description: Turn bug bounty recon, JavaScript parsing results, API evidence, parameters, hidden routes, and business logic signals into ranked, testable vulnerability hypotheses and exploit paths. Use when Codex needs to infer likely vuln classes, reason about exploitability, separate evidence from assumptions, design safe validation steps, assess impact, reduce false positives, or prepare a bug bounty report outline.
---

# Vuln Triage Reasoner

## Triage Principles

Do not overclaim. A vulnerability hypothesis needs a clear asset, actor, action, missing control, expected result, exploit path, and impact path.

Rank by likely impact and verifiability, not by keyword excitement. Prefer one strong, reproducible issue over many weak guesses.

## Exploit Reasoning Policy

When evidence suggests a bug, actively infer how exploitation would work if the suspected server-side control is missing. This reasoning should be concrete enough for authorized validation, but not weaponized.

Allowed exploit reasoning and validation:

- Request templates with placeholders for cookies, tokens, object IDs, tenant IDs, emails, and reversible test values.
- Read-only checks, self-account checks, cross-account checks using user-owned authorized test accounts, and reversible state changes.
- Clear expected secure behavior, vulnerable signal, and stop conditions.
- Running a minimal validation request when authorization, scope, accounts, and safe test data are available.
- Promoting reproduced issues to confirmed findings with exact request/response evidence.

Do not produce operational exploit steps that steal data, alter another real user's account, bypass payment for real services, persist access, brute force credentials/tokens, exploit third-party infrastructure, or cause disruption. In those cases, provide a bounded safe validation plan instead.

## Validate Then Promote

If a hypothesis is strong and the user has provided sufficient authorization context, validate it before final triage.

Required validation gates:

- Explicit in-scope asset.
- Test class allowed by program rules.
- User-owned account/session/token, or a public unauthenticated endpoint where validation is non-invasive.
- User-owned target objects, tenants, carts, files, orders, emails, webhooks, redirects, or reversible workflow items.
- One clear baseline request and one manipulated request, unless a single request is enough for an information disclosure finding.
- Stop condition that prevents unauthorized data access, irreversible state change, real payment impact, third-party impact, or service disruption.

Promotion rules:

- `Confirmed`: vulnerable behavior reproduced with exact request/response, timestamp/context, and impact using authorized data.
- `Ready`: fileable without exploit execution, such as exposed source maps with `sourcesContent`, public debug metadata, or verified non-sensitive exposure.
- `Needs test`: exploit path is credible but validation was not run or lacked required context.
- `Weak`: signal lacks reachability, control boundary, or impact.
- `Discarded`: server enforced the control, asset was out of scope, behavior is expected, or validation would be unsafe.

## Reasoning Loop

1. Normalize evidence.
   - List endpoints, methods, params, roles, object IDs, auth requirements, state changes, and business workflows.

2. Map to control families.
   - Authorization: IDOR/BOLA, BFLA, tenant isolation, role bypass.
   - Input handling: injection, file upload, SSRF, open redirect, path traversal, mass assignment.
   - Session/browser: CORS, CSRF, token exposure, OAuth/OIDC flow issues.
   - Business logic: pricing, coupon/refund, invite/team, approval workflow, quota/rate, export/import.
   - Information exposure: debug endpoints, source maps, secrets candidates, internal metadata.

3. Build hypotheses.
   - Phrase as "If server does not enforce X, then actor Y can do Z against object W."
   - Attach exact evidence and missing proof.

4. Build exploit path.
   - Chain each strong hypothesis as: `actor -> precondition -> manipulated request -> missing server control -> vulnerable signal -> impact`.
   - Identify the exploit primitive: ID swap, tenant swap, role/status/plan field edit, hidden route replay, GraphQL mutation replay, redirect/webhook URL control, upload/import abuse, mass assignment, CORS/CSRF browser pivot, or source-map information disclosure.
   - State what proof is still missing.
   - Prefer placeholders and user-owned test objects over live values.

5. Design validation.
   - Use scoped accounts and low-impact objects.
   - Start with read-only or reversible actions where possible.
   - Specify expected secure response and vulnerable response.
   - Include a minimal PoC only when it is safe, authorized, and based on concrete evidence.
   - Prefer request templates with placeholders for cookies, object IDs, and tenants instead of live secrets.

6. Validate and promote.
   - Execute minimal safe validation when the gates are satisfied.
   - Compare baseline and manipulated responses.
   - Promote confirmed vulnerabilities to finding drafts.
   - Keep unvalidated exploit paths as hypotheses.

7. Decide report readiness.
   - `Confirmed`: reproduced with evidence and impact.
   - `Ready`: fileable non-invasive exposure.
   - `Needs test`: strong path but not reproduced.
   - `Weak`: speculative keyword or no reachable endpoint.
   - `Discard`: out of scope, third party, expected behavior, or blocked by server control.

## Output Format

```markdown
## Run Summary
- Scope:
- Evidence sources:
- Tools/evidence used:
- Ready findings:
- Confirmed findings:
- Needs-test hypotheses:
- Weak/discarded items:
- Required user input:

## Biggest Finds
1. Finding:
   - Affected asset:
   - Evidence:
   - Status:
   - Why it matters:

## Ranked Hypotheses
| Rank | Status | Class | Finding/Hypothesis | Evidence | Exploitability / PoC | Safe validation | Impact if confirmed |

## Exploit Paths
| Rank | Status | Actor | Preconditions | Exploit chain | Missing proof | Stop conditions |

## Validation Results
| Rank | Test | Baseline evidence | Manipulated evidence | Decision | Finding status |

## Best Next Test
- Target:
- Actor/account:
- Request:
- Expected secure behavior:
- Vulnerable signal:
- Safety notes:

## Exploitability / Safe PoC
### PoC: <finding title>
- Status: Confirmed / Ready / Needs test / Weak / Discarded
- Exploit chain:
- Preconditions:
- Why exploitation may be possible:
- Minimal safe request:
- Baseline evidence:
- Manipulated request evidence:
- Expected secure behavior:
- Vulnerable behavior if confirmed:
- Stop conditions:

## Concrete Finding Drafts
### Finding: <title>
- Status: Confirmed / Ready / Needs test
- Affected asset:
- Vulnerability class:
- Evidence:
- Reproduction:
- Exploitability:
- Safe PoC:
- Security impact:
- Reproduction or validation plan:
- Remediation:

## Report Outline If Confirmed
- Title:
- Summary:
- Steps:
- Impact:
- Remediation:

## Discarded / Deprioritized
```

## References

Read [references/vuln-mapping.md](references/vuln-mapping.md) for evidence-to-vulnerability mapping and false positive checks.
