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

Allowed exploit reasoning:

- Request templates with placeholders for cookies, tokens, object IDs, tenant IDs, emails, and reversible test values.
- Read-only checks, self-account checks, cross-account checks using user-owned authorized test accounts, and reversible state changes.
- Clear expected secure behavior, vulnerable signal, and stop conditions.

Do not produce operational exploit steps that steal data, alter another real user's account, bypass payment for real services, persist access, brute force credentials/tokens, exploit third-party infrastructure, or cause disruption. In those cases, provide a bounded safe validation plan instead.

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

6. Decide report readiness.
   - `Ready`: reproduced with evidence and impact.
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

## Best Next Test
- Target:
- Actor/account:
- Request:
- Expected secure behavior:
- Vulnerable signal:
- Safety notes:

## Exploitability / Safe PoC
### PoC: <finding title>
- Status: Ready / Needs test / Weak
- Exploit chain:
- Preconditions:
- Why exploitation may be possible:
- Minimal safe request:
- Expected secure behavior:
- Vulnerable behavior if confirmed:
- Stop conditions:

## Concrete Finding Drafts
### Finding: <title>
- Status: Ready / Needs test
- Affected asset:
- Evidence:
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
