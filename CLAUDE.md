# Bug Bounty Skills Workspace

This repository contains reusable bug bounty hunting skills. When working in this folder, treat each `*/SKILL.md` file as an operational playbook and load the related `references/` file only when it is relevant to the user request.

## Available Skills

- `recon-hunter/`: Map authorized scope, assets, technologies, URLs, JS artifacts, API surfaces, and recon priorities.
- `js-parser-hunter/`: Extract endpoints, API paths, params, functions, GraphQL operations, storage keys, secret candidates, and business keywords from JavaScript/frontend artifacts.
- `js-logic-analyst/`: Analyze frontend JavaScript behavior for hidden logic, role checks, feature gates, workflow rules, and business logic vulnerability leads.
- `vuln-triage-reasoner/`: Turn recon/JS/API evidence into ranked, testable vulnerability hypotheses, exploit reasoning, and safe validation plans.

## How To Use These Skills

1. Identify the user's task and select the matching skill:
   - Recon/scope/asset mapping -> read `recon-hunter/SKILL.md`.
   - JS extraction/parsing -> read `js-parser-hunter/SKILL.md`.
   - JS behavior/business logic analysis -> read `js-logic-analyst/SKILL.md`.
   - Vulnerability reasoning/exploit path/triage/report outline -> read `vuln-triage-reasoner/SKILL.md`.

2. Read the skill's `SKILL.md` first.

3. Load the referenced file under `references/` only if the task needs deeper signal mapping.

4. Keep a strict boundary between:
   - Evidence: observed request, response, code, URL, parameter, status, role, account, timestamp.
   - Inference: likely meaning of the evidence.
   - Hypothesis: a testable vulnerability idea that still needs validation.
   - Exploit reasoning: a concrete but unconfirmed path from actor, precondition, request, missing server-side control, vulnerable signal, and impact.

5. Do not claim a vulnerability is confirmed unless the agent or user has reproduction evidence. If the user has supplied authorized scope, program rules, and suitable test accounts/objects, the agent may run safe validation and promote confirmed results to findings.

6. When JavaScript analysis reveals bug-like signals, automatically reason about exploitability. Do not stop at "interesting endpoint." For each strong signal, derive:
   - Actor and privilege level required.
   - Object or tenant boundary involved.
   - Client-side control that may be bypassed.
   - Server-side control that must be tested.
   - Minimal safe request or browser action with placeholders.
   - Expected secure behavior and vulnerable signal.
   - Impact if confirmed and stop conditions.

## Output Language

Default all user-facing output to Vietnamese.

Use Vietnamese for:

- Recon summaries, triage reasoning, exploit paths, findings, impact, remediation, assumptions, open questions, and follow-up plans.
- Report section prose and table explanations.
- Status explanations such as `Confirmed`, `Ready`, `Needs test`, `Weak`, and `Discarded`.

Keep these values in their original language/format:

- URLs, endpoints, HTTP methods, headers, params, cookies, JSON keys, code identifiers, file paths, tool names, command output, request/response snippets, vulnerability class names, and program rule quotes.
- Standard bug bounty terms where English is clearer, such as IDOR/BOLA, BFLA, SSRF, CSRF, CORS, OAuth, GraphQL, source map, mass assignment, open redirect.

If the user explicitly requests English or another language for a specific report, follow that request for that output only.

## Required User Input

Ask for missing context when needed. The best inputs are:

- Authorized scope: domains, wildcard domains, apps, APIs, mobile apps, excluded assets.
- Program rules: out-of-scope tests, rate limits, destructive action restrictions, third-party restrictions.
- Goal: broad recon, JS endpoint discovery, IDOR/BOLA, auth bypass, business logic, GraphQL, secrets, report writing.
- Artifacts: JS files, bundle URLs, source maps, HAR files, Burp requests/responses, API docs, sitemap, archived URLs.
- Account context: number of test accounts, roles, tenants/orgs/workspaces, permissions.
- Current evidence: endpoint, method, params, headers, status code, response body, suspected issue.

## Autonomous Tool Use

When the user asks for recon, JS analysis, endpoint discovery, API testing, parameter discovery, business logic review, vulnerability triage, or exploit reasoning from JS evidence, infer the next useful step and use available local tools without waiting for explicit tool-by-tool instructions.

Before running network-active tools, verify that authorized scope and program rules are known. If scope is missing or ambiguous, ask for it first. If a command may be intrusive, high-volume, destructive, authenticated, or outside normal safe validation, ask before running it.

Prefer this order:

1. Local/passive evidence first: files, JS bundles, source maps, HAR, Burp exports, URLs, API docs, archived URL lists.
2. Low-impact verification second: DNS resolution, HTTP liveness, headers, status code, single endpoint checks.
3. Focused crawling/fuzzing third: only against confirmed in-scope assets and with conservative rate/wordlist choices.
4. Vulnerability validation last: use safe, minimal, reversible test cases with user-provided accounts/tokens.

Exploit reasoning is allowed before validation, but only as a bounded analysis artifact. Keep exploit content scoped to authorized targets, use placeholders for credentials/object IDs, and prefer read-only or reversible test cases. If the likely exploit would require stealing data, changing another user's account, bypassing payment for real services, credential attacks, persistence, or disruption, output a safe validation plan instead of operational exploit steps.

### Exploit Validation To Finding

When a strong hypothesis has enough authorization context, validate it instead of stopping at theory.

Allowed validation requirements:

- The asset is explicitly in scope.
- Program rules do not prohibit the test class.
- The request is low-impact, reversible, or read-only.
- Authentication material is user-provided or captured from the user's own authorized session.
- Object IDs, tenants, emails, files, webhooks, redirects, orders, carts, invoices, and roles used in the test belong to the user or authorized test accounts.
- The validation has clear stop conditions before accessing unauthorized data, causing real financial effects, or changing production state irreversibly.

Validation loop:

1. Build the minimal request or browser action from evidence.
2. Execute one controlled baseline request when needed.
3. Execute one manipulated request that tests the missing server-side control.
4. Compare status code, response body shape, headers, object ownership, and state change.
5. If the vulnerable signal is observed, mark the item `Ready` and write a finding draft.
6. If the server blocks it, mark `Discarded` or `Weak` with the exact blocking evidence.
7. If proof would require unsafe impact, stop and keep it as `Needs test` with a safe validation plan.

Finding promotion criteria:

- `Confirmed`: reproduced with exact request/response evidence and clear impact using authorized test data.
- `Ready`: fileable without invasive testing, such as source map exposure, public debug metadata, or verified non-sensitive information exposure.
- `Needs test`: exploit path is strong but not reproduced.
- `Weak`: signal exists but lacks reachability, auth context, or impact.
- `Discarded`: out of scope, blocked by server control, duplicate, expected behavior, or unsafe to validate.

### Tool Selection Rules

Use whichever appropriate tools exist locally. Do not assume a fixed ProjectDiscovery-only stack. On Kali Linux, first inventory the local toolset with `command -v` or `which`, then choose the lightest tool that fits the evidence and program rules.

Tool choice must be context-aware:

- Passive recon: prefer local files, supplied artifacts, `rg`, `jq`, `waybackurls`, `gau`, `github-search` style evidence, certificate/DNS data, and archives before active probing.
- Live host discovery: prefer `httpx`, `curl`, `dnsx`, `dig`, `massdns`, or equivalent tools already installed.
- Crawling/JS collection: prefer `katana`, `hakrawler`, `gospider`, browser exports, sitemap/robots parsing, and archive URLs depending on scope and rate limits.
- Web content discovery: use `ffuf`, `feroxbuster`, `dirsearch`, `gobuster`, or similar only when focused, rate-limited, and allowed.
- API testing: prefer `curl`, `httpie`, Burp exports, Postman/OpenAPI files, `jq`, and custom minimal request replay.
- Template checks: use `nuclei` only with scoped targets and safe templates/severity filters.
- Mobile analysis: use public app metadata first; use APK/IPA tools such as `apktool`, `jadx`, `aapt`, `mobSF`, `strings`, or `grep/rg` only when app files are provided or retrieval is authorized.
- Secret scanning: use deterministic local scanning first (`rg`, parser output, `trufflehog`, `gitleaks` if present) and redact full values.
- Exploit validation: prefer manual, minimal, reversible requests over automated exploit frameworks.

When multiple tools can do the same job, choose by safety and evidence quality:

1. User-provided/local artifacts.
2. Passive public data.
3. Single-request verification.
4. Conservative crawling.
5. Focused fuzzing/template checks.
6. Manual safe validation.

Record tool decisions in the report: tools used, purpose, important options, tools skipped, and why.

On Windows/Codex Desktop, if `python` or `python3` is not in PATH, use the bundled Python runtime reported by the workspace dependency loader. In this workspace, the verified fallback is:

```powershell
& 'C:\Users\killn\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' js-parser-hunter\scripts\js_extract.py <args>
```

| Task | Preferred tools | Use when |
| --- | --- | --- |
| Parse local/remote JS | `python3 js-parser-hunter/scripts/js_extract.py` | JS files, bundles, source maps, URL lists, frontend artifacts are available |
| Inspect text/code | `rg`, `find`, `sed`, `jq` | Searching endpoints, params, secrets candidates, GraphQL, route tables |
| Subdomain discovery | `subfinder`, `amass` | Program allows recon on wildcard/root domain |
| DNS resolution | `dnsx`, `massdns`, `dig` | Need to separate live/resolving hosts from noise |
| HTTP probing | `httpx`, `curl` | Need status, title, redirects, headers, technologies |
| Crawling | `katana`, `hakrawler` | Need URLs/JS from confirmed in-scope web apps |
| Archived URLs | `gau`, `waybackurls` | Need historical endpoints and old parameters |
| URL normalization | `uro`, `unfurl`, `qsreplace` | Need dedupe, parameter extraction, URL shaping |
| Directory/param fuzzing | `ffuf` | Only focused, rate-limited, in-scope, non-destructive discovery |
| Template checks | `nuclei` | Only safe templates and scoped targets; avoid intrusive templates unless explicitly allowed |
| Request replay | `curl`, `httpie`, Burp exports | Verify specific endpoint behavior from evidence |
| JSON/API handling | `jq`, `yq` | Parse API responses, OpenAPI specs, GraphQL JSON |
| Kali alternatives | `feroxbuster`, `dirsearch`, `gobuster`, `gospider`, `httpie`, `apktool`, `jadx`, `aapt`, `trufflehog`, `gitleaks` | Use only when installed, in scope, and better suited than the default tool |

### Default Safe Command Patterns

Use conservative defaults unless the user specifies otherwise:

```bash
subfinder -d example.com -silent
httpx -l hosts.txt -title -tech-detect -status-code -follow-redirects -silent
katana -list live.txt -jc -kf all -silent
gau example.com
waybackurls example.com
python3 js-parser-hunter/scripts/js_extract.py ./js --json
python3 js-parser-hunter/scripts/js_extract.py --url-list js_urls.txt --scope-domain example.com --json
```

For fuzzing, keep it narrow:

```bash
ffuf -u https://target.example/FUZZ -w wordlist.txt -rate 20 -mc all -fs <known_baseline_size>
```

For `nuclei`, prefer safe severity filters and explicit target files:

```bash
nuclei -l live.txt -severity low,medium,high,critical -rl 20
```

Do not run broad port scanning, high-rate fuzzing, exploit templates, credential attacks, brute force, destructive state changes, or DoS-style tests unless the user explicitly confirms that the program allows them.

## JS Parser Command

When the user provides local JS files or a directory, run:

```bash
python3 js-parser-hunter/scripts/js_extract.py <file-or-directory> --json
```

When the user provides a JS URL list, run:

```bash
python3 js-parser-hunter/scripts/js_extract.py --url-list <js-url-list> --scope-domain <authorized-domain> --json
```

The parser discovers source maps by default using `sourceMappingURL` and common implicit paths such as `app.js.map`. Keep source map fetching in scope. If the program does not allow fetching source maps, add `--no-discover-source-maps`.

Use the output as evidence for `js-logic-analyst` or `vuln-triage-reasoner`.

For a human-readable report:

```bash
python3 js-parser-hunter/scripts/js_extract.py <file-or-directory>
```

## Recommended Workflows

### Full Recon To Hypothesis

1. Read `recon-hunter/SKILL.md`.
2. Build scope and asset priorities.
3. Collect JS/API artifacts.
4. Run `js-parser-hunter/scripts/js_extract.py` on JS artifacts.
5. Read `js-logic-analyst/SKILL.md` for complex frontend behavior.
6. Read `vuln-triage-reasoner/SKILL.md` to produce ranked hypotheses and safe validation steps.

### JS Bundle Analysis

1. Read `js-parser-hunter/SKILL.md`.
2. Run the parser on the bundle/source map directory.
3. Cluster endpoints by feature area and business action.
4. Read `js-logic-analyst/references/business-logic-patterns.md` for role/plan/workflow clues.
5. For every P1/P2 signal, derive an exploit path: actor -> precondition -> request shape -> missing server control -> vulnerable signal -> impact.
6. Produce endpoint tables, hidden logic signals, exploitability notes, and testable hypotheses.

### Vulnerability Triage

1. Read `vuln-triage-reasoner/SKILL.md`.
2. Normalize evidence into actor, asset, action, object, control, and impact.
3. Build exploit chains from the strongest JS/API signals before ranking.
4. Rank by impact, evidence quality, exploitability, and verifiability.
5. Output a minimal safe test plan with expected secure behavior and vulnerable signal.

## Required Report Contract

For recon, JS crawling, JS parsing, endpoint discovery, business logic analysis, or vulnerability triage tasks, produce a concrete report. Do not stop at raw tool output. The report must include a high-signal executive summary and enough evidence for the user to continue testing in Burp/browser.

Use this exact top-level structure when writing `work/js_report.md` or a final Markdown report:

```markdown
# Bug Bounty Recon Report

## Run Summary

Scope (in-scope only): <domains actually treated as in scope>

Tools actually used: <tool names plus purpose and important options>

Tools available but not required: <tools found but not used, with reason>

Tools missing / fallbacks: <missing/broken tools and fallback used>

JS URL pipeline:
- <raw URLs crawled/collected> raw URLs -> <JS hits> JS hits -> <unique JS URLs> unique JS URLs -> <in-scope JS URLs> in-scope -> <parsed count> fed to parser
- <saved file count> files saved to <path> when applicable
- <source map count> source maps found/parsed, note whether `sourcesContent` was present

Biggest finds:
1. <specific finding, affected host/path, evidence, status>
2. <specific finding, affected host/path, evidence, status>
3. <specific finding, affected host/path, evidence, status>

Artifacts:
- <path>: <what it contains>

Top open follow-ups:
- <concrete next action and what evidence/input is needed>
```

Then include detailed sections:

```markdown
## 1. Methodology And Tool Notes
### 1.1 Scope Handling
### 1.2 Tools Run
### 1.3 Tool Failures / Fallbacks

## 2. JS Corpus And Source Maps
| Host | JS/source map URL | Status | Hash | Evidence | Notes |

## 3. Extracted API And Logic Surface
| Priority | Host/source | Endpoint or signal | Method hint | Params | Evidence | Why it matters |

## 4. Ranked Hypotheses
| Rank | Status | Class | Finding/Hypothesis | Evidence | Exploitability / PoC | Safe validation | Impact if confirmed |

## 5. Exploit Validation And Findings
### PoC: <finding title>
- Status: Confirmed / Ready / Needs test / Weak / Discarded
- Exploit chain: <actor -> precondition -> request/control bypass -> vulnerable signal -> impact>
- Preconditions: <required account, role, tenant, object ownership, token, feature flag>
- Why exploitation may be possible: <specific missing server-side control inferred from evidence>
- Minimal safe request or browser steps: <non-destructive validation only>
- Baseline evidence:
- Manipulated request evidence:
- Expected secure behavior:
- Vulnerable behavior if confirmed:
- Safety limits:

## 6. Confirmed Finding Drafts
### Finding: <title>
- Status: Confirmed / Ready
- Affected asset:
- Vulnerability class:
- Evidence:
- Reproduction steps:
- Exploitability:
- Security impact:
- Safety notes:
- Remediation:

## 7. Follow-Up Plan
| Priority | Action | Needed input | Tool/manual path |

## 8. Final Summary
- Tìm được gì:
- Finding confirmed/ready:
- Hypothesis cần test:
- Điểm bị loại hoặc bị server chặn:
- Cần làm gì thêm:
- Input cần từ user:

## Appendix: Raw Counts
```

Status values:

- `Confirmed`: reproduced during this run or by user-provided evidence with exact request/response proof and clear impact.
- `Ready`: enough evidence to file as information disclosure or a clear non-invasive issue.
- `Needs test`: strong hypothesis, not reproduced yet.
- `Weak`: interesting but speculative.
- `Discarded`: out of scope, blocked by server control, duplicate, expected behavior, or insufficient evidence.

Finding quality rules:

- Name exact host/path/file/function/param whenever possible.
- Include source file or URL and line/context when available.
- Include count-based pipeline metrics from tool output, not vague words like "many".
- Redact full secrets. Show provider/type, short prefix/suffix, source file, and verification needed.
- For source maps, state whether production `.map` returned `200`, whether original source is present, and whether `sourcesContent` is included.
- For API/business logic hypotheses, include the missing server-side control being tested.
- Never mark BOLA/IDOR/CSRF/mass assignment as confirmed without validation evidence.
- Include exploitability details when evidence supports them, but keep PoCs minimal, scoped, non-destructive, and reproducible with user-owned test accounts.
- Do not provide PoCs that steal data, bypass payment for real services, alter other users' accounts, persist access, brute force credentials/tokens, exploit third-party infrastructure, or cause service disruption.
- If a potentially exploitable path requires privileged credentials, victim interaction, destructive state change, or access to another user's data, output a safe validation plan instead of a weaponized exploit.

Final summary rules:

- End every report with a concise Vietnamese summary.
- State what was actually found, not just what was scanned.
- Separate `confirmed/ready findings`, `needs-test hypotheses`, `weak leads`, and `discarded/blocked items`.
- Include the exact next actions needed to turn hypotheses into findings.
- Mention missing inputs such as test accounts, roles, tenant pairs, auth tokens, HAR/Burp traffic, APK/IPA files, or program-rule clarification.
- If nothing significant was found, say that clearly and list the highest-value follow-ups.

## Safety Rules

- Work only on authorized targets and user-provided artifacts.
- Do not suggest destructive tests unless the program explicitly permits them.
- Avoid social engineering, credential theft, persistence, malware, or production disruption.
- Redact full secret values; show short prefixes/suffixes and evidence location.
- Prefer low-impact validation using the user's own test accounts and reversible objects.
- Exploit/PoC content must be framed for authorized bug bounty validation and must include preconditions, expected secure behavior, vulnerable signal, and stop conditions.
