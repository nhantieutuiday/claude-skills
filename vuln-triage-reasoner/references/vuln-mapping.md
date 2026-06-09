# Vulnerability Mapping

## Evidence -> Candidate Class

- Sequential or user-controlled object IDs -> IDOR/BOLA, tenant isolation failure.
- Role/action strings in request body -> mass assignment, role bypass, BFLA.
- `redirect`, `returnUrl`, `callback`, `next` -> open redirect, OAuth flow abuse.
- Webhook/fetch/import URL -> SSRF, URL parser confusion, internal network access.
- Upload/import/template/file/path -> file upload abuse, parser injection, path traversal.
- GraphQL operations and introspection hints -> broken object authorization, excessive data exposure, batching/rate bypass.
- CORS with credentials or broad origins -> cross-origin data access risk.
- Source maps, debug endpoints, stack traces -> information exposure, secret leakage.
- Coupon/refund/invoice/subscription flows -> business logic abuse.

## Hypothesis Template

`If <missing server control>, then <actor> can <unauthorized action> on <object/scope>, causing <impact>.`

## Exploit Path Template

Use this after every strong hypothesis:

`<actor> with <precondition> sends <request manipulation> against <object/scope>. If <server control> is missing, the vulnerable signal is <response/state change>, causing <impact>.`

Example placeholders:

- Actor: anonymous, normal user, lower-tier user, org member, tenant admin, partner user.
- Preconditions: two authorized test accounts, two authorized tenants, owned object IDs, reversible object, valid session, feature flag visible in JS.
- Request manipulation: change `id`, change `tenantId`, add `role`, replay hidden endpoint, change `status`, call GraphQL mutation, set redirect URL, submit webhook URL.
- Vulnerable signal: 200/201/204, forbidden object data returned, role/status changed, export generated, callback fired, server accepts hidden field, lower-tier feature executes.
- Stop conditions: 401/403/404 normalized denial, server ignores field, irreversible action required, real user/payment/third-party impact, rate limit hit.

## Safe PoC Rules

- Use placeholders for auth headers, cookies, object IDs, tenant IDs, emails, URLs, and request bodies.
- Prefer `GET`, `HEAD`, dry-run flags, preview endpoints, self-owned objects, and reversible changes.
- For cross-account testing, require two user-owned authorized accounts or tenants.
- For payment, refund, role, destructive workflow, webhook, SSRF, upload, or import paths, provide the minimum non-destructive validation signal and stop before impact.
- Never include live secrets, victim identifiers, brute force logic, persistence, disruption steps, or instructions to access data outside authorization.

## Report Readiness Checklist

- Scoped asset and program rule alignment.
- Reproduction steps with timestamps and accounts.
- Exact request/response evidence.
- Clear expected secure behavior.
- Business impact in terms of data, money, privilege, or availability.
- No unnecessary sensitive data exposure in the report.

## Finding Promotion Checklist

Promote a hypothesis to a finding only when one of these is true:

- `Confirmed`: validation was reproduced using authorized test data and includes baseline evidence, manipulated evidence, vulnerable signal, and impact.
- `Ready`: the issue is directly observable without invasive exploitation, such as exposed source maps with original source, public debug metadata, or public non-sensitive information exposure with clear security relevance.

Do not promote when:

- The only evidence is a JS string or endpoint name.
- Server-side authorization has not been tested and impact depends on it.
- The test would require another real user's data, real payment/refund, destructive workflow, brute force, persistence, social engineering, or third-party impact.
- The server returns 401/403/404, ignores sensitive fields, recomputes sensitive values, or otherwise enforces the expected control.

For confirmed findings, include:

- Target URL/host and exact endpoint.
- Account/role context, without secrets.
- Baseline request summary.
- Manipulated request summary.
- Response/status/body difference.
- Impact using authorized data.
- Stop condition observed or respected.
- Remediation mapped to the missing server-side control.

## Common Discards

- Endpoint string exists but is not reachable.
- Third-party service is out of scope.
- Client-side key is intentionally public and restricted.
- Server denies unauthorized object/action.
- Impact requires social engineering, destructive testing, or policy-prohibited actions.
