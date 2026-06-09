---
name: js-parser-hunter
description: Parse and analyze JavaScript files, bundles, source maps, and frontend artifacts during authorized bug bounty recon. Use when Codex needs to extract endpoints, API paths, routes, domains, parameters, hidden functions, feature flags, GraphQL operations, storage keys, tokens/secrets candidates, business actions, or security-relevant strings from JS.
---

# JS Parser Hunter

## Quick Start

For local files or directories, run:

```bash
python3 js-parser-hunter/scripts/js_extract.py <path> --json
```

For a list of JS URLs, run:

```bash
python3 js-parser-hunter/scripts/js_extract.py --url-list js_urls.txt --scope-domain example.com --json
```

The parser discovers source maps by default from `sourceMappingURL` comments and common implicit paths such as `app.js.map`. Use `--no-discover-source-maps` only when source map fetching is not allowed by scope or program rules.

Use the JSON output as evidence, then reason about:

- Endpoint reachability and auth boundary.
- Parameter names and object identifiers.
- Hidden routes, feature flags, and admin/internal wording.
- Security-sensitive browser storage, headers, tokens, and GraphQL operations.
- Business actions such as billing, invite, role, refund, export, import, approval, or impersonation.
- Exploitability signals: client-supplied roles, object IDs, tenant IDs, workflow states, prices, coupon/refund fields, redirect URLs, webhook URLs, upload/import paths, GraphQL mutations, and disabled UI actions that still construct complete requests.

## Workflow

1. Inventory files and URLs.
   - Prefer original source maps when available.
   - Keep bundle filename, URL, hash, and collection timestamp.
   - For remote JS, keep status code, final URL, content type, and scope-domain filtering evidence.

2. Extract deterministic signals.
   - Run `scripts/js_extract.py` on bundles, source trees, a single URL, or `--url-list`.
   - Preserve raw matches for endpoints, domains, params, functions, storage keys, GraphQL, secrets candidates, and business keywords.

3. De-minify mentally, not cosmetically.
   - Identify request wrappers, API clients, route tables, permission checks, feature gates, and state stores.
   - Trace where extracted strings are used before assuming impact.

4. Group findings.
   - Cluster by API base path, feature area, role boundary, object type, and state-changing verb.
   - Mark each item as `direct evidence`, `inferred`, or `needs dynamic validation`.
   - For P1/P2 items, add an `exploit cue`: the likely actor, target object, missing server control, and safe validation style.

5. Escalate analysis.
   - Use `$js-logic-analyst` when the JS contains complex auth, role, pricing, workflow, or validation logic.
   - Use `$vuln-triage-reasoner` when enough evidence exists to form vulnerability hypotheses or exploit paths.

## Output Format

```markdown
## JS Parser Run Summary
- Scope domains:
- Input URLs/files:
- Raw/crawled URLs:
- JS hits:
- Unique JS URLs:
- In-scope JS URLs:
- Parsed JS/source map artifacts:
- Source maps found:
- Source maps with sourcesContent:
- Fetch failures / skipped URLs:
- Saved artifacts:

## Extracted API Surface
| Priority | Host/source | Endpoint | Method hint | Params | Evidence | Why it matters | Validation |

## Hidden / Interesting Logic
| Priority | Signal | Source | Evidence | Exploit cue | Why it matters | Next test |

## Sensitive Candidates
| Type | Redacted value | Source | Confidence | Required verification |

## Source Map Exposure
| URL | Status | sourcesContent | Original sources | Evidence | Filing status |

## Hypotheses To Send To Triage
- Include actor, object boundary, suspected missing server-side control, and a safe validation idea for each P1/P2 hypothesis.

## Final Summary
- Tìm được gì:
- Endpoint/logic đáng chú ý nhất:
- Hypothesis cần test:
- Cần làm gì thêm:
- Input cần từ user:
```

## References

Read [references/js-signal-taxonomy.md](references/js-signal-taxonomy.md) for signal categories and prioritization rules.
