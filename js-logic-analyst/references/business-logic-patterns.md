# Business Logic Patterns

## Frontend Signal -> Server Question

- Hidden button by role -> Does the API enforce role server-side?
- Disabled action by status -> Can the request be replayed in a forbidden workflow state?
- Plan/tier gate -> Can a lower-tier account call the endpoint directly?
- Client-side price/quantity/coupon calculation -> Does the server recompute totals and constraints?
- Object ID in route/body -> Does the server enforce ownership and tenant isolation?
- Invite/team management -> Can users escalate roles, invite outside policy, or accept stale invites?
- Export/import -> Are authorization, file type, parser limits, and data boundaries enforced?
- Webhook URL -> Is SSRF, scheme restriction, DNS rebinding, or internal metadata access controlled?
- Redirect/callback -> Is destination allowlisted and bound to OAuth/session state?

## Strong Vulnerability Leads

- Same endpoint accepts object IDs not present in UI.
- UI blocks an action but the request schema contains all fields needed to perform it.
- Role, plan, status, or tenant fields are sent by the client.
- Admin/internal routes share the same API base as normal user routes.
- Source maps expose original module names around permissions, billing, or workflow engines.

## Exploit Primitive Patterns

For each strong lead, write the exploit path as a bounded hypothesis:

`actor -> precondition -> request manipulation -> missing server control -> vulnerable signal -> impact`

- Hidden role action: normal user replays admin route -> missing role check -> 2xx/state change -> privilege boundary bypass.
- Object ownership: user A swaps `objectId` to user B's authorized test object -> missing ownership check -> data returned or state changes -> IDOR/BOLA.
- Tenant boundary: tenant A swaps `tenantId/orgId/workspaceId` to tenant B's authorized test tenant -> missing tenant isolation -> cross-tenant data/action.
- Plan gate: lower-tier user calls enterprise endpoint directly -> missing entitlement check -> feature executes -> paid feature bypass.
- Workflow gate: user replays approve/cancel/submit endpoint after UI disables it -> missing state-machine check -> invalid transition accepted.
- Mass assignment: user adds hidden `role/status/plan/isAdmin` field -> server accepts client-controlled sensitive field -> privilege/state manipulation.
- Price/coupon/refund: user changes price, quantity, coupon, refund amount, or invoice target -> server trusts client value -> financial impact.
- Redirect/callback: user controls destination -> missing allowlist/session binding -> open redirect or OAuth callback abuse.
- Webhook/import URL: user supplies controlled URL -> missing scheme/host/IP restrictions -> SSRF-style behavior or unsafe fetch.

## False Positive Checks

- Server returns 401/403 or normalized 404 for unauthorized objects.
- Server recomputes sensitive values and ignores client-supplied role/price/status.
- Feature is intentionally public or documented.
- The route exists only in dead code or a disabled build branch.
- The action requires destructive effects, real payment impact, third-party abuse, or another real user's data; switch to safe validation planning.
