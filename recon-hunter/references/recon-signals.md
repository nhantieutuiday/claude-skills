# Recon Signals

## Priority Signals

Rank higher when an asset has:

- Authenticated app surfaces, dashboards, admin panels, partner portals, SSO flows, or account/team management.
- API hosts with state-changing routes, object IDs, exports, imports, uploads, webhooks, billing, coupons, refunds, invites, approvals, or role changes.
- JavaScript bundles exposing route tables, source maps, internal API names, feature flags, or GraphQL operations.
- Legacy stacks, debug headers, staging wording, old archive URLs, forgotten subdomains, or inconsistent auth behavior.
- Cross-boundary concepts: tenant, organization, workspace, project, account, user, team, role, permission, invoice, subscription.

## Deprioritize

- Parked domains, marketing-only pages, strict third-party SaaS, duplicate CDN aliases, static assets without interesting JS, and endpoints clearly outside program scope.

## Recon Evidence Quality

- Strong: live request/response, scoped host, timestamp, reproducible URL, clear auth state.
- Medium: archived URL, JS string with reachable base path, documentation mention.
- Weak: keyword only, unresolved host, out-of-date archive, third-party ownership unclear.

## Next-Action Mapping

- Many object IDs or tenant terms -> hand to `$vuln-triage-reasoner` for IDOR/BOLA hypotheses.
- Rich JS bundles or source maps -> hand to `$js-parser-hunter`.
- Complex UI role or plan logic -> hand to `$js-logic-analyst`.
- Upload/import/export/webhook surfaces -> prioritize file handling, SSRF, parser abuse, and authorization checks.
