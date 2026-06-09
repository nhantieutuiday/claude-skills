---
name: recon-hunter
description: Professional bug bounty reconnaissance workflow for authorized targets. Use when Codex needs to map scope, assets, subdomains, technologies, exposed services, URLs, JavaScript files, historical content, API surfaces, attack surface priority, and recon findings for a bug bounty or security testing engagement.
---

# Recon Hunter

## Operating Rules

Work only from explicit authorized scope. Treat out-of-scope hosts, third-party SaaS, customer tenants, and production-destructive actions as excluded unless the program rules clearly allow them.

Separate facts, inferences, and hypotheses. Never label an issue as vulnerable without enough evidence to reproduce or a clear next test.

## Workflow

1. Normalize scope.
   - Extract root domains, wildcard domains, mobile apps, API hosts, IP ranges, excluded paths, forbidden test classes, and rate limits.
   - Record program-specific constraints before suggesting tools or tests.

2. Build the asset graph.
   - Enumerate subdomains, resolved hosts, CDN edges, cloud buckets, certificate names, ASN/IP ranges, app stores, GitHub orgs, documentation portals, status pages, and support domains.
   - Mark each asset as `in_scope`, `probably_related`, `third_party`, or `out_of_scope`.

3. Fingerprint live surfaces.
   - Capture status code, title, server, framework, WAF/CDN, auth state, interesting headers, cookies, CSP, CORS, cache headers, and redirect chains.
   - Cluster similar hosts to avoid duplicate analysis.

4. Collect URLs and client artifacts.
   - Gather crawled URLs, archived URLs, sitemap/robots links, OpenAPI/GraphQL hints, source maps, JavaScript bundles, mobile deep links, and documentation examples.
   - Hand JavaScript-heavy artifacts to `$js-parser-hunter` and behavior-heavy artifacts to `$js-logic-analyst`.

5. Prioritize attack surface.
   - Rank assets by business criticality, authentication boundary, state-changing endpoints, admin/partner/internal hints, file upload/import/export, payment/billing, user role logic, object IDs, and legacy technology.
   - Prefer reachable, scoped, reproducible paths over noisy volume.

6. Produce a recon dossier.
   - Include scope interpretation, asset inventory, priority targets, evidence links/files, unresolved questions, and next tests.
   - Hand consolidated evidence to `$vuln-triage-reasoner` for ranked vulnerability hypotheses.

## Output Format

Use this structure for final recon output:

```markdown
## Scope Read
- In scope:
- Excluded / risky:
- Assumptions:

## High-Value Assets
| Priority | Asset | Evidence | Why it matters | Next step |

## Interesting Surfaces
| Surface | Signals | Candidate tests |

## JS / API Artifacts
| File or URL | Signals | Send to |

## Open Questions

## Next Recon Commands
```

## References

Read [references/recon-signals.md](references/recon-signals.md) when ranking discovered assets or translating recon signals into next actions.
