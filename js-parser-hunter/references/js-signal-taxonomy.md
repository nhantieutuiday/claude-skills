# JS Signal Taxonomy

## Endpoint Signals

- Absolute URLs: `https://api.example.com/v1/users`.
- Relative API paths: `/api/`, `/v1/`, `/graphql`, `/rest/`, `/admin/`.
- Route templates: `/users/:id`, `/orgs/{orgId}`, template literals with IDs.
- Request wrappers: `fetch`, `axios`, `XMLHttpRequest`, `graphql-request`, custom API clients.

## Parameter Signals

Prioritize params that imply object ownership or control decisions:

- `userId`, `accountId`, `orgId`, `tenantId`, `workspaceId`, `projectId`.
- `role`, `permission`, `isAdmin`, `plan`, `tier`, `status`, `state`.
- `redirect`, `returnUrl`, `next`, `url`, `callback`, `webhook`.
- `file`, `path`, `key`, `bucket`, `template`, `query`, `filter`.

## Hidden Logic Signals

- Feature flags: `enable`, `beta`, `experiment`, `internal`, `adminOnly`.
- Business actions: `refund`, `coupon`, `invoice`, `subscription`, `invite`, `approve`, `export`, `impersonate`.
- Environment hints: `staging`, `dev`, `debug`, `localhost`, `internal`, `sandbox`.

## Exploit Cue Mapping

Use these cues to decide whether to send a signal to `$js-logic-analyst` or `$vuln-triage-reasoner`.

- Object IDs in route/body/query -> test ID swap with user-owned objects; expected control is ownership and tenant isolation.
- `tenantId`, `orgId`, `workspaceId`, `accountId` -> test cross-tenant boundary using two authorized test tenants.
- `role`, `permission`, `isAdmin`, `adminOnly` -> test direct route replay or body-field tampering; expected control is server-side role enforcement and ignored client roles.
- `plan`, `tier`, `subscription`, `license`, `quota` -> test lower-tier direct call with self account; expected control is server-side entitlement enforcement.
- `price`, `coupon`, `discount`, `refund`, `invoice`, `quantity` -> test server recomputation with harmless cart/test item; expected control is server-side totals and policy enforcement.
- `status`, `state`, `approve`, `cancel`, `workflow` -> test replay in invalid state on user-owned object; expected control is server-side state-machine enforcement.
- `redirect`, `returnUrl`, `next`, `callback` -> test allowlist with benign external URL; expected control is strict destination binding.
- `webhook`, `url`, `importUrl`, `fetchUrl` -> test URL validation with a controlled collaborator-style endpoint only if rules allow; expected control is scheme/host/IP allowlist and no internal fetch.
- `upload`, `file`, `path`, `template`, `import` -> test file type, path, parser, and authorization boundaries with inert payloads only.
- GraphQL mutations -> test mutation replay and object/tenant ID changes with user-owned objects; expected control is resolver-level authorization.

## Secret Candidate Rules

Treat secret-looking strings as candidates until verified. Avoid dumping full secrets in reports; show short prefixes/suffixes and evidence location.

High confidence: private key blocks, cloud access key patterns, long bearer tokens, webhook signing secrets.

Medium confidence: API key names, JWT-like strings, DSNs, public SDK keys.

Low confidence: hashes, bundle IDs, random-looking CSS/module hashes.
