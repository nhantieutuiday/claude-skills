# Acronis JS Recon & Triage Report

**Date:** 2026-06-09
**Scope (in-scope only):** `www.acronis.com`, `*.acronis.com`
**Engagement type:** Authorized bug bounty – recon + static analysis only
**Mode:** Low-impact crawling & fetching; no login, no fuzz, no destructive tests

> Evidence is split into three layers per `CLAUDE.md`:
> 1. **Evidence** – observed request, response, code, URL, parameter, status, role, account, timestamp.
> 2. **Inference** – likely meaning of the evidence.
> 3. **Hypothesis** – a testable vulnerability idea that still needs validation. No vulnerability is marked "confirmed" here.

---

## 1. Recon Hunter (recon-hunter)

### 1.1 Scope Read

- **In scope:**
  - `www.acronis.com`
  - `*.acronis.com` (any subdomain)
- **Excluded / risky:**
  - Third-party SaaS observed in JS (e.g. `force.com`, `salesforce.com`, `marketo.net`, `cloudfront.net`, `googletagmanager.com`, `wday.com`, `visualwebsiteoptimizer.com`, `recaptcha.net`) – out of scope.
  - Production-destructive actions, brute force, fuzzing, exploit templates – not run (per user rules).
  - Authentication with credentials – not available, so no logged-in testing performed.
- **Assumptions:**
  - Public marketing and product surfaces are in scope. CDN edges and language-redirect pages are still `*.acronis.com`, so they are in scope.
  - "Customer tenants" of `cloud.acronis.com` are *not* authorized to test – this report only touches public assets, not authenticated console endpoints.
  - `care.acronis.com` is the public Acronis community site (Salesforce-backed). It is a *.acronis.com host, so it is in scope, but we treat any Salesforce-internal endpoints referenced as out-of-scope test targets.

### 1.2 Tools Used (after local check)

| Tool | Status | Use |
| --- | --- | --- |
| `katana` (homebrew) | ✅ | Crawl seed URLs with JS extraction, depth 2, low rate |
| `curl` | ✅ | Probe single URLs, head checks, wayback CDX attempts |
| `httpx` | ✅ | Liveness / status probes (used only for spot checks, not full sweep) |
| `python3` | ✅ | js-parser-hunter script; post-processing of saved JS |
| `rg` (ripgrep) | ✅ | Extract JS URLs from crawl output, filter scope |
| `subfinder` | ✅ | Subdomain enumeration (100+ hosts enumerated) |
| `dnsx` | ✅ | Available; not required for this pass |
| `qsreplace` | ✅ | Available; not required for this pass |
| `hakrawler` | ❌ not installed | Fallback: katana covers crawl |
| `gau` | ❌ aliased to `git add` | Fallback: Wayback CDX attempted; rate-limited; relied on katana for live crawl |
| `waybackurls` | ❌ not installed | Fallback: Wayback CDX API attempted; see note below |

### 1.3 Wayback CDX note

`https://web.archive.org/cdx/search/cdx?url=acronis.com&matchType=domain&filter=mimetype:application/javascript` returned **HTTP 429 Too Many Requests** across multiple retries (with 60s+ waits). We did not bypass with rotating headers / multiple source IPs because that would be disproportionate to the rules. Live katana crawl is the primary URL source for this run. Re-attempting wayback with a longer cooldown and a single non-Safari UA at a later time is a low-cost follow-up.

### 1.4 Asset Graph (in scope)

| Asset | Type | What we observed | Source |
| --- | --- | --- | --- |
| `www.acronis.com` | Marketing site | 73 JS URLs crawled (main bundles, 404 page, language variants) | `katana` crawl |
| `academy.acronis.com` | Customer training portal (Vue 3 + Vuex SPA) | 9 JS URLs; full app source map decoded (`app-BOvFy2C8.js.map`) | `katana` crawl |
| `connect.acronis.com` | Partner / reseller portal | 15 JS URLs (React, Redux, react-intl, react-router); mostly vendor | `katana` crawl |
| `care.acronis.com` | Community / support (Salesforce Experience Cloud) | 16 JS URLs; many Salesforce `auraFW` & `aura_prod.js`; some short URLs filtered out due to filename length | `katana` crawl |
| `promo.acronis.com` | Marketing promo / stripmkt | 4 JS URLs (`stripmkttok.js`) | `katana` crawl |
| `a.acronis.com` | GTM container host | `https://a.acronis.com/ns.html?id=GTM-PFG6ZF` referenced from www 404 | hardcoded URL extracted |
| `account.acronis.com` | Account login | referenced from www 404 | hardcoded URL extracted |
| `cloud.acronis.com` | Product console (login) | referenced from www 404 | hardcoded URL extracted |
| `learn.acronis.com` | Learning portal | referenced from www 404 | hardcoded URL extracted |
| `partners.acronis.com` | Partner login | referenced from www 404 | hardcoded URL extracted |
| `staticfiles.acronis.com` | Static CDN | referenced from www 404 | hardcoded URL extracted |
| `websiteapi.acronis.com` | Marketing CMS API | referenced from www 404 | hardcoded URL extracted |

Also enumerated 100+ subdomains via `subfinder` (sample: `info`, `beta-s3gw`, `go.jp-cloud`, `rs-eu8-cloud`, `affiliate`, `branded-ae01-cloud`, `de99-cloud`, `docs`, `office`, `acep`, `ru-edge-1`, `za01-cloud`, `br02-cloud`, `my01-cloud`, `osl1-repo`, `spmp.corp`, …). These are listed in `work/subfinder_acronis.txt`. Liveness/role classification was not done in this pass; treat as `probably_related` until proven `in_scope` for any further testing.

### 1.5 High-Value Assets

| Priority | Asset | Evidence | Why it matters | Next step |
| --- | --- | --- | --- | --- |
| P1 | `academy.acronis.com` | Source map decoded; original Vue/TS code visible (`/api/finance/licenses`, `/svc/v1/cleverbridge/surl`, `/svc/v1/marketing/forms/leads`, `ProductAPIQueryBuilder`, `cleverbridge`, `licenses`, `inapp`, `pages`, `config`, `express-signup`, `promotion`) | Public site exposing **full source code** + **internal product API paths** + **payment flow** | Static code review (this report); low-impact GET to confirm reachability of `/api/finance/licenses` and `/svc/v1/cleverbridge/surl` |
| P1 | `www.acronis.com` 404 / main JS | Hardcoded subdomain list (a, account, cloud, connect, learn, partners, staticfiles, websiteapi); GTM `GTM-PFG6ZF`; VWO; Workday | Marketing site gives the **full subdomain map** and **third-party integration list** | Done (static) |
| P2 | `connect.acronis.com` (partner portal) | 15 JS URLs; React + react-intl + react-router-redux | Likely partner login + portal – common BOLA / BFLA surface | Need authenticated test accounts; static analysis only this run |
| P2 | `care.acronis.com` | Salesforce `auraFW`, `aura_prod.js`, `esw.min.js` (embedded chat), `RecordGVP.js`, `ContentAssetGVP.js` | Salesforce Experience Cloud; embedded service; if misconfigured could leak internal org data | Liveness/headers check; out of scope for deeper exploit attempts |
| P3 | `promo.acronis.com` | `stripmkttok.js` (Marketo strip) | Marketing tracking; minor | Static only |

### 1.6 Interesting Surfaces (candidates)

| Surface | Signal | Candidate test (low impact) |
| --- | --- | --- |
| `POST /svc/v1/cleverbridge/surl` (academy) | withCredentials: true; `validateStatus: (s) => s===200`; data is `Record<string, any>` (mass assignment?) | Authenticated POST; check whether client-supplied fields propagate to billing |
| `POST /svc/v1/marketing/forms/leads` (academy) | `timeout: 30s`, no auth evident in client | Unauthenticated POST of lead form data; check rate limiting and field validation |
| `GET /api/finance/licenses` (academy) | Uses `ProductAPIQueryBuilder` with `cleverbridge_id`, `locale`, `currency` filters | Authenticated GET; check if filter params are honored server-side vs. overwritten |
| `ProductAPIQueryBuilder` (c-core-essentials) | `addMatchesAll`, `addMatchesAny`, `setOutputExcept(FIELDS_EXCEPT)` (mass assignment concern) | If `addMatchesAll` is forwarded verbatim, test SQLi/noSQL injection and access-control bypass |
| Source map exposure (academy, academy chunks) | `.js.map` files returned `200 OK` with full `sourcesContent` (43 + 245 sources) | Information disclosure – flag as low-severity report (or low-priority "best practice") |
| Google API keys in `api-keys.ts` | `GOOGLE_MAP_API_KEY`, `GOOGLE_SEARCH_API_KEY`, reCAPTCHA site key, `GOOGLE_SEARCH_CX_KEY` | Test each key against the respective Google APIs to confirm it is restricted by HTTP referrer (Maps, reCAPTCHA enterprise, Custom Search) |
| `HEAD_SITE_MAIN_FEATURE_CLIENT_IGNORE_SSL_ERRORS` | Env-driven; controls whether HTTPS agent ignores SSL errors | Confirmed default-off expected; not exploitable as is – informational |
| Workday link in `www.acronis.com` 404 | `https://services1.wd502.myworkday.com` (careers) | Out of scope |

### 1.7 JS / API Artifacts

Saved to `work/js_fetched/` (292 files: bundles + source maps). `work/parser.json` (22 MB) contains the full parser output (URL fetches, source map scans, summary).

---

## 2. JS Parser Hunter (js-parser-hunter)

### 2.1 JS Corpus

- **Files scanned:** 301 (incl. 14 successfully fetched `.js.map`)
- **URLs (final input list):** 106 (`work/js_urls_short.txt`) – filtered to in-scope `*.acronis.com` only.
  - The full initial katana list had 130 unique JS URLs; 13 third-party domains (`googletagmanager`, `salesforceliveagent`, `marketo`, `cloudfront`, `force.com`, `salesforce.com`) were excluded; 11 long Salesforce `care.acronis.com/s/sfsites/...` URLs were excluded from the *save-to-disk* pass (file-name length) but the bundle URL itself was excluded as a third-party-ish Salesforce Experience Cloud path (Salesforce, not Acronis). Static analysis on this subset is sufficient for the recon-hunter phase.
- **Source maps:** 207 map entries; 14 fetched (status 200) and decoded; `sourcesContent` present in academy maps.
- **URL fetch notes:** All in-scope. No 4xx/5xx on first attempt within `*.acronis.com` (one Salesforce long-URL was rejected locally due to filesystem path length, not server error).
- **Collection notes:** Single run; no second wave. No UA rotation.

### 2.2 Extracted API Surface (deterministic)

| Endpoint | Method hint | Params | Evidence | Validation status |
| --- | --- | --- | --- | --- |
| `/api/press-releases/press-releases/` | GET (list) | (built by `ProductAPIQueryBuilder`) | `app-BOvFy2C8.js` + its `.js.map` | Needs test (low-impact GET) |
| `/api/blog/posts/` | GET | `section_id`, `has[products]`, `locale` | `app-BOvFy2C8.js` / source map | Needs test |
| `/api/blog/posts/views/` | POST | post id | `app-BOvFy2C8.js` | Needs test |
| `/api/core/popups` | GET | (popup id filters) | `app-BOvFy2C8.js` | Needs test |
| `/api/core/products/` | GET | locale filters | `app-BOvFy2C8.js` | Needs test |
| `/api/core/ribbons` | GET | (locale) | `app-BOvFy2C8.js` | Needs test |
| `/api/customers/companies` | GET | (locale filters) | `app-BOvFy2C8.js` | Needs test |
| `/api/events/events/` | GET | (locale) | `app-BOvFy2C8.js` | Needs test |
| `/api/finance/licenses` | GET | `matches-all`: `locale`, `currency`, `cleverbridge_id`; `process-macros=1`; `output[except]`; `paginate` | `licenses.ts` source map – see snippet below | Needs test (likely authenticated) |
| `/api/finance/price-lists/` | GET | locale | `app-BOvFy2C8.js` | Needs test |
| `/api/finance/price-lists/prices` | GET | locale, list id | `app-BOvFy2C8.js` | Needs test |
| `/api/finance/promotions/` | GET | locale | `app-BOvFy2C8.js` | Needs test |
| `/api/finance/promotions/translations/` | GET | locale | `app-BOvFy2C8.js` | Needs test |
| `/api/resources/resources/` | GET | (locale) | `c-core-essentials` source map | Needs test |
| `/v2/account` | GET (list-style) | (account id) | `app-BOvFy2C8.js` | Needs test (auth) |
| `/v2/account/agreement` | GET | account id | `app-BOvFy2C8.js` | Needs test |
| `/v2/auth/login` | POST | (login form) | `app-BOvFy2C8.js` | Needs test (auth) |
| `/v2/auth/logout` | POST | – | `app-BOvFy2C8.js` | Needs test (auth) |
| `/v2/auth/register` | POST | (register form) | `app-BOvFy2C8.js` | Needs test (auth) |
| `/v2/products/trial` | POST | (trial form) | `app-BOvFy2C8.js` | Needs test |
| `POST /svc/v1/cleverbridge/surl` | POST | `Record<string, any>` | `cleverbridge.ts` source map | Needs test (auth + payment) |
| `POST /svc/v1/marketing/forms/leads` | POST | `Record<string, any>` | `express-signup.ts` source map | Needs test (likely unauth) |

Notes:
- All `/api/...` endpoints are constructed by `ProductAPIQueryBuilder` from `c-core-essentials.js.map` -> `src/api/builders/product.ts`. The builder is a fluent client; many list endpoints are generated this way.
- `/v2/...` and `/svc/v1/...` paths come from a different client (`getAPIService`); we have not yet confirmed the base URL since it is loaded from `context.public.env.HEAD_SITE_MAIN_PUBLIC_BASE_URL_*`. The base URL itself is an interesting static-discovery follow-up (need to find the SSR-rendered `window.__NUXT__` or pre-rendered DOM env to learn the host).

### 2.3 Source-Map-Verified Code (key evidence)

From `academy.acronis.com .../app-BOvFy2C8.js.map` -> `sourcesContent`:

**`src/api/product.ts`** (product API client):
```ts
const baseURL = typeof window === 'undefined'
    ? context.public.env.HEAD_SITE_MAIN_PUBLIC_BASE_URL_PRODUCT_API_SERVER
    : context.public.env.HEAD_SITE_MAIN_PUBLIC_BASE_URL_PRODUCT_API_CLIENT;
const instance = axios.create({ ...defaults, baseURL, ... });
// then: AssignHttpsAgent, WrapAxiosWithRequestLogger, ObservePromAPILatency
```

**`src/vue3/store/modules/cleverbridge.ts`** (payment):
```ts
const options = {
    method: 'POST',
    url: '/svc/v1/cleverbridge/surl',
    timeout: 30000,
    validateStatus: (status) => status === StatusCodes.OK,
    data,
    withCredentials: true,
};
const response = await client.request(options);
```

**`src/vue3/store/modules/express-signup.ts`** (marketing leads):
```ts
const cfg = {
    timeout: 30 * 1000,
    validateStatus: () => true,
    method: 'POST',
    url: '/svc/v1/marketing/forms/leads',
    data,
};
```

**`src/vue3/store/modules/licenses.ts`** (license listing):
```ts
const payload = new ProductAPIQueryBuilder('licenses')
    .addMatchesAll('locale', '=', locale)
    .addMatchesAll('currency', '=', currency)
    .addMatchesAll('cleverbridge_id', 'in', cleverbridgeIDs)
    .setCustomParam('process-macros', '1')
    .setOutputExcept(FIELDS_EXCEPT)
    .setPaginate(paginate.number, paginate.size)
    .toObject();

const options = {
    method: 'GET',
    params: payload.params,
    url: '/api/finance/licenses',
    validateStatus: (status) => status === StatusCodes.OK,
};
```

**`src/model/const/api-keys.ts`** (frontend constants):
```ts
export const GOOGLE_MAP_API_KEY = 'AIzaSyBjxiXjlbfwB6XYedcmed29xNKQlQPbIAM';
export const RECAPTCHA_ENTERPRISE_INVISIBLE_KEY = '6LcMQSEjAAAAAPWFRMLg7n6NERJhIndKRAbBcoKo';
export const RECAPTCHA_SCRIPT_SRC = 'https://www.google.com/recaptcha/enterprise.js?render=explicit';
export const RECAPTCHA_SCRIPT_SRC_CHINA = 'https://www.recaptcha.net/recaptcha/enterprise.js?render=explicit';
export const GOOGLE_SEARCH_CX_KEY = '368730cd75f71415a';
export const GOOGLE_SEARCH_API_KEY = 'AIzaSyBx70YZuWyyzRfP22ZBpFqLrosyrYrzg08';
```

**`src/utils/api-response.ts`** (response handling):
```ts
export function convertToConsumableObjects(responseData, privateFields) {
    return responseData.map((x) => {
        const picked = omit(x, privateFields);
        const pairs = Object.entries(picked)
            .map((pair) => [camelCase(pair[0]), pair[1]]);
        return Object.fromEntries(pairs);
    });
}
```

**`src/api/builders/product.ts`** (query builder – relevant to mass assignment / injection):
```ts
class ProductAPIQueryBuilder {
    addMatchesAll(field, operator, value) { ... }
    addMatchesAny(field, operator, value) { ... }
    setOutputExcept(fields) { ... }
    setOutputOnly(fields) { ... }
    setPaginate(number, size) { ... }
    setCustomParam(key, value) { ... }
}
```

### 2.4 Hidden / Interesting Logic

| Signal | Evidence | Why it matters | Next test |
| --- | --- | --- | --- |
| `validateStatus: () => true` in client axios defaults (everywhere) | `product.ts` and `express-signup.ts` source maps | Client never throws on non-2xx; success/failure detection is delegated to caller. Means **server-side status codes are not enforced by the client** – good for the bug hunter because the client will still forward the body on 4xx/5xx, so data leak signals in error bodies are easier to observe. | Read full response bodies on all calls. |
| `HEAD_SITE_MAIN_FEATURE_CLIENT_IGNORE_SSL_ERRORS` | env var passed to `AssignHttpsAgent` | Configurable SSL verification bypass on client side. If a user can be MITM'd or if an env override can be injected, traffic to product API can be intercepted. | Confirm default value (likely `false`); check whether the env can be overridden by user-controlled input. |
| `withCredentials: true` on `/svc/v1/cleverbridge/surl` | `cleverbridge.ts` | Cookie auth + state-changing endpoint. Classic CSRF surface. | Check whether server validates `Origin` / a CSRF token; if not, **CRLF / state-changing CSRF** on the surl-generation endpoint. |
| `ProductAPIQueryBuilder` accepts arbitrary field names and operators | `product.ts` builder | The `addMatchesAll('field','op','value')` pattern is client-controlled. If the server forwards this verbatim to a downstream filter, attacker may be able to filter on internal fields (e.g. `is_admin`, `partner_tier`, `internal`) they should not be able to influence. Also classic injection vector if the server concatenates. | Authenticated GET to `/api/finance/licenses?matches-all[0][0]=...&matches-all[0][1]=...` and observe server behavior. |
| `setOutputExcept(FIELDS_EXCEPT)` | `licenses.ts` defines `FIELDS_EXCEPT = ['alias', 'created_at', 'created_by', 'id', 'updated_at']` | **Mass-assignment direction:** the client **only** omits those fields. If the server honors this `output[except]` parameter (e.g. via JSON-API sparse fieldsets), an attacker can request `output[except]=` (empty) and force the server to return the full record including `id`, `created_by`, etc. | Authenticated GET with manipulated `output[except]`. |
| ReCAPTCHA Enterprise site key + Google Maps API key + Google Custom Search API key + CX key in client bundle | `api-keys.ts` | These are public-by-design for browser use. **Action:** confirm each is restricted by HTTP referrer / domain in the Google Cloud Console. If a key is unrestricted, an attacker can use it to bill the Acronis Google Cloud project (Custom Search has a free quota; Maps is also metered). | Use the keys against `https://www.google.com/maps/...` and `https://customsearch.googleapis.com/...` from an off-scope host. |
| `partnersLocator` and `partners` keywords | `app` source map names list | Likely a public partner-search feature. Worth checking IDOR/BOLA on the lookup. | Unauthenticated GET on the partner locator; check rate limit. |
| `/admin`, `/internal`, `/debug` paths in `site-header` | `site-header.D22XXGnV.js.map` regex hits – **53 matches per file** | These are the **header** JS, so they are likely just the strings used in UI hints / dev mode. The exact paths and gating need a closer look at the source map. | Decode the `site-header` source map and confirm whether `/admin` etc. are routes, redirects, or just banned/internal banners. |
| `connect.acronis.com/login/` | hardcoded in `www.acronis.com` 404 | Confirms `connect` is a partner portal. Public redirect. | Liveness check (auth not in scope yet). |
| `acronis_sfchat_maximized` localStorage key | `c-core-essentials` source map | Embedded Salesforce chat widget state. Not sensitive, just informational. | – |

### 2.5 Sensitive Candidates

| Type | Value snippet | Confidence | Required verification |
| --- | --- | --- | --- |
| Google API key (reCAPTCHA enterprise) | `AIzaSy…bIAM` (full value redacted) | High it's a real key (decoded from `api-keys.ts`) | Confirm key is **referrer-restricted** in Google Cloud. Public use is expected. |
| Google Custom Search API key | `AIzaSy…zg08` | High | Same as above. Check CSE API key restrictions and CX key validity. |
| Google Custom Search Engine ID | `368730cd75f71415a` | High (CX key, not a secret) | Verify which domains the CX is configured to search. |
| reCAPTCHA Enterprise invisible site key | `6LcMQSEj…` (full value redacted) | High (site key – not a secret) | Verify Enterprise console shows the expected domains only. |

> No bearer tokens, AWS access keys, or private keys were found in any of the 292 saved JS / source-map files.

### 2.6 Hypotheses To Triage

- (carried forward to §4)

---

## 3. JS Logic Analyst (js-logic-analyst)

For each business action we identified, we list: feature boundary, evidence trace, candidate vulnerability, and false-positive checks.

### 3.1 Feature: License listing (`/api/finance/licenses`)

- **Feature:** Customer-facing license listing filtered by `cleverbridge_id` and locale/currency.
- **Roles / tenants:** Authenticated customer. Tenant = Acronis account / partner. Boundary is the logged-in user.
- **Business rule:** Each user should only see licenses for their own account/tenant. Filter is by `cleverbridge_id` from a known set (likely tied to the user).
- **Evidence trace:**
  - `licenses.ts` -> `addMatchesAll('cleverbridge_id', 'in', cleverbridgeIDs)` — the IDs come from the **store** (`store.getters.licenses.data`), which the caller passes in.
  - `ProductAPIQueryBuilder` -> fluent builder that constructs `params.matches-all`.
  - `FIELDS_EXCEPT` = `['alias', 'created_at', 'created_by', 'id', 'updated_at']` — client asks the server to omit these. But `id` and `created_by` are *sensitive* (ownership, audit). The client still excludes them, but the server is the source of truth.
- **Client-side decision → server question:**
  - "The client only ever sends `cleverbridge_id` values from the store" → does the server **trust** `matches-all[cleverbridge_id, in, ...]` verbatim, or does it re-scope by the authenticated user?
  - "The client excludes `id` and `created_by`" → does the server **allow** the client to override field visibility, or does it always return a fixed schema?
- **Candidate vulnerability:** BOLA / IDOR if the server trusts client-supplied filters; information disclosure if `output[except]=` (empty) yields full row including `id` and `created_by`.
- **False-positive check:** Server may filter internally based on auth context. The `matches-all` array may be honored only for fields the server knows the user is allowed to filter on. `output[except]` may be ignored server-side.
- **Minimal safe test (if test accounts are available):**
  - Authenticated GET to `/api/finance/licenses?matches-all[0][0]=cleverbridge_id&matches-all[0][1]=in&matches-all[0][2]=<other_user_id>&output[except]=` and compare with the unfiltered response.

### 3.2 Feature: Cleverbridge payment URL generation (`/svc/v1/cleverbridge/surl`)

- **Feature:** Generate a Cleverbridge "secure URL" used to start a purchase flow.
- **Roles / tenants:** Authenticated customer. Possibly also pre-authenticated trial flows.
- **Business rule:** SURL is per-session, scoped to the user, and price/currency must come from server-side catalog.
- **Evidence trace:**
  - `cleverbridge.ts` -> `POST /svc/v1/cleverbridge/surl`, `data: Record<string, any>` (the client passes the whole record through).
  - `withCredentials: true` (cookie auth).
  - `validateStatus: (s) => s===200` (client only treats 200 as success; non-200 returns `null`).
- **Client-side decision → server question:**
  - "Client can pass any fields in `data`" → does the server **whitelist** which fields it accepts? Can a client inject `price=0`, `coupon=…`, `partner_id=…`?
  - "Cookie auth, no CSRF token evident in this call" → does the server check `Origin` / a CSRF token, or is the cookie + `Content-Type` enough? `application/json` with `text/plain` CORS preflight?
- **Candidate vulnerability:** Price/coupon manipulation if server accepts client-supplied price/coupon; CSRF if not.
- **False-positive check:** Server may re-price based on the authenticated user and ignore client-supplied price fields. The cookie may be `SameSite=Lax` or `Strict`, which mitigates CSRF on top-level navigations.
- **Minimal safe test:** Requires authenticated session. Send `POST /svc/v1/cleverbridge/surl` with a manipulated `data` and observe whether the response contains the manipulated price/coupon.

### 3.3 Feature: Express signup / marketing lead form (`/svc/v1/marketing/forms/leads`)

- **Feature:** Marketing lead capture (express signup).
- **Roles / tenants:** Anonymous / pre-auth.
- **Business rule:** Server should validate email/phone format, deduplicate, throttle by IP.
- **Evidence trace:**
  - `express-signup.ts` -> `POST /svc/v1/marketing/forms/leads`, `data: Record<string, any>`, no auth header.
  - `validateStatus: () => true` (no client-side status check).
- **Client-side decision → server question:**
  - "No auth required" → can the form be **submitted unauthenticated**? (Likely yes – this is a lead form.)
  - "Free-form `data`" → can the client **inject extra fields** that the server stores? (Mass assignment / stored XSS in CRM downstream?)
  - "No rate-limit logic in client" → is there server-side rate limiting?
- **Candidate vulnerability:** Stored XSS / lead poisoning if the lead is rendered without sanitization in an internal CRM; SMS / email enumeration if the form confirms whether an email is already known.
- **False-positive check:** Marketing forms are usually hardened. Salesforce / Marketo endpoints typically store the payload as-is into a CRM where sanitization may be in place.
- **Minimal safe test:** Unauthenticated POST to `/svc/v1/marketing/forms/leads` from a single IP with a minimal payload; observe response. Do not spam.

### 3.4 Feature: Auth endpoints (`/v2/auth/login`, `/v2/auth/logout`, `/v2/auth/register`, `/v2/account`, `/v2/account/agreement`)

- **Feature:** Authentication and account management.
- **Evidence trace:** Paths observed in `app-BOvFy2C8.js` source map.
- **Candidate vulnerability:** Standard login enumeration, password-reset poisoning, account-takeover via `redirect_uri` / `returnUrl`.
- **False-positive check:** Standard auth hardening likely in place.
- **Next step:** Look for a `redirect_uri` / `next` parameter in the actual login flow; static analysis only this pass.

### 3.5 Feature: Product API builder (cross-cutting)

- **Feature:** Universal list/filter builder used by every `/api/...` endpoint on academy.
- **Candidate vulnerability:** Mass assignment / parameter pollution / injection (if the builder's `addMatchesAll('field', 'op', 'value')` is forwarded as a JSON-object param to the server, the server's filter interpreter decides what is honored).
- **Next step:** With test account: authenticated GET to `/api/blog/posts/?matches-all[0][0]=status&matches-all[0][1]=&matches-all[0][2]=internal` to see if internal posts are exposed.

### 3.6 Feature: Source-map exposure

- **Feature:** Static asset exposure (`*.js.map` returns 200 with `sourcesContent`).
- **Candidate vulnerability:** Information disclosure. The `app-BOvFy2C8.js.map` returns **43 sources of original TypeScript**, including the API client config, env var names, business action names, etc. An attacker can:
  1. Read the source offline to find logic bugs.
  2. Map internal modules (`@api/builders/product`, `@model/const/api-keys`) to plan more targeted tests.
- **Severity:** Low. This is not a "vulnerability" in the OWASP sense, but it is a common bounty finding (information disclosure / hardening).
- **Next step:** If the program accepts it, file as a "source maps exposed in production" report. Suggest generating source maps only in non-prod or using a separate URL (e.g. `/_internal/sourcemaps/...`).

---

## 4. Vuln Triage Reasoner (vuln-triage-reasoner)

We normalize the JS evidence and produce **ranked, testable hypotheses**. None are confirmed.

### 4.1 Ranked Hypotheses

| # | Class | Hypothesis | Evidence | Test (minimal) | Impact if confirmed | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Source-map disclosure** | Production JS files at `academy.acronis.com/.../*.js.map` return `200 OK` with `sourcesContent` containing full original TypeScript source. | `app-BOvFy2C8.js.map` (200, 198 KB, 43 sources), `c-core-essentials.js.map` (200, 245 sources), and 12 more. | `curl -I https://academy.acronis.com/dist/site-client/assets/app-BOvFy2C8.js.map` | Low. Information disclosure, helps every later test, and is a common "best-practice" bounty finding. | **Ready** (we already have the file). |
| 2 | **BOLA / IDOR on license listing** | If the server trusts client-supplied `matches-all[cleverbridge_id, in, …]`, an authenticated user can list licenses for other customers. | `licenses.ts` -> `addMatchesAll('cleverbridge_id', 'in', cleverbridgeIDs)`. | Authenticated GET to `/api/finance/licenses?matches-all[0][0]=cleverbridge_id&matches-all[0][1]=in&matches-all[0][2]=<other_user>`. | High (license disclosure, customer data). | Needs test (requires 2 test accounts). |
| 3 | **Mass assignment / field over-posting on Cleverbridge surl** | Client posts `data: Record<string, any>` to `/svc/v1/cleverbridge/surl`; if the server doesn't whitelist fields, attacker can override price/coupon/partner_id. | `cleverbridge.ts` -> `data, withCredentials: true`. | Authenticated POST to `/svc/v1/cleverbridge/surl` with `data: { price: 0, coupon: 'STAFF' }`. | High (revenue impact, free purchases, partner attribution). | Needs test (requires account). |
| 4 | **CSRF on Cleverbridge surl** | Cookie-authed state-changing POST without visible CSRF token; if `SameSite` is `None` and the server doesn't check `Origin`, a cross-site form can trigger it. | `withCredentials: true`; no `csrf`/`xsrf` keyword in `cleverbridge.ts` or surrounding modules. | Inspect `Set-Cookie` header on a fresh session for `SameSite` attribute; check pre-flight response. | High (silent checkout initiation). | Needs test (cookie inspection). |
| 5 | **Information disclosure via `output[except]` override** | Client uses `setOutputExcept(FIELDS_EXCEPT)` where `FIELDS_EXCEPT` includes `id` and `created_by`; if the server honors this filter param, sending `output[except]=` (empty) returns the full row. | `licenses.ts` `FIELDS_EXCEPT` array; `ProductAPIQueryBuilder.setOutputExcept`. | Authenticated GET with `output[except]=` and observe `id` / `created_by` in response. | Medium (audit trail, owner email leak). | Needs test (requires account). |
| 6 | **Filter parameter injection in `ProductAPIQueryBuilder`** | `addMatchesAll('field', 'op', 'value')` forwards arbitrary field/operator/value to the server; if the server's filter interpreter is loose, attacker can filter on internal fields (`is_admin`, `partner_tier`, etc.) they should not influence. | `product.ts` builder source. | Authenticated GET `matches-all[0][0]=partner_tier&matches-all[0][1]==&matches-all[0][2]=gold`. | Medium-High depending on what surfaces. | Needs test (requires account). |
| 7 | **Google API key abuse** | `GOOGLE_MAP_API_KEY` / `GOOGLE_SEARCH_API_KEY` / `GOOGLE_SEARCH_CX_KEY` are in the client bundle; if not restricted by HTTP referrer in Google Cloud, anyone can use them, billing Acronis. | `api-keys.ts` source map. | From an off-scope host, call `https://maps.googleapis.com/maps/api/...` and `https://customsearch.googleapis.com/customsearch/v1?key=…&cx=…`. | Medium (financial). | Ready (keys in hand). |
| 8 | **Marketing form abuse / lead poisoning** | `/svc/v1/marketing/forms/leads` accepts free-form `data` unauthenticated; if downstream CRM doesn't sanitize, attacker can store XSS in lead notes. | `express-signup.ts` source map. | Single unauth POST with a `<script>` payload in a free-text field. | Medium (CRM XSS -> phishing / data theft of internal users). | Needs test (don't spam). |
| 9 | **`/admin`, `/internal`, `/debug` paths** | Source map for `site-header` contains 53 hits per file for these paths. Need to confirm whether they are reachable routes, redirects, or just strings. | `site-header.D22XXGnV.js.map` regex match. | Decode the `site-header` source map for the 53 contexts and identify each occurrence; then probe the live site. | Variable. | Needs test (decode + probe). |
| 10 | **Trial endpoint state-change** | `POST /v2/products/trial` – trial activation. If not idempotent or not auth-scoped, attacker could start a trial in another user's name. | `app-BOvFy2C8.js` API table. | Authenticated POST `/v2/products/trial`; observe response and server-side check on user identity. | Medium (license abuse). | Needs test (requires account). |

### 4.2 Best Next Test (one)

> **Target:** Source-map disclosure on `academy.acronis.com` (hypothesis #1).
> **Actor / account:** none (unauthenticated).
> **Request:**
> ```bash
> curl -sI https://academy.acronis.com/dist/site-client/assets/app-BOvFy2C8.js.map
> curl -s  https://academy.acronis.com/dist/site-client/assets/app-BOvFy2C8.js.map | head -c 200
> ```
> **Expected secure behavior:** `404 Not Found` or `403 Forbidden`, or the file exists but `sourcesContent` is stripped.
> **Vulnerable signal:** `200 OK` with `Content-Type: application/json; charset=utf-8` and a non-empty body containing the `sourcesContent` array.
> **Safety notes:** Read-only; no state change. Already executed in this recon (`work/js_fetched/academy.acronis.com_dist_site-client_assets_app-BOvFy2C8.js.map.faec5352a5` is 198 KB, 43 sources). Treat as **Ready** to file as an information-disclosure / hardening report.

### 4.3 Report Outline If Confirmed (template for #1)

- **Title:** Production source maps expose original TypeScript / Vue source on `academy.acronis.com`.
- **Summary:** Several `.js.map` files on `*.acronis.com` (academy + main) return `200 OK` with `sourcesContent` populated, leaking the full original source code of the Academy SPA including internal module names (`@api/builders/product`, `@model/const/api-keys`, `@utils/env`), env-var names (`HEAD_SITE_MAIN_PUBLIC_BASE_URL_PRODUCT_API_*`, `HEAD_SITE_MAIN_FEATURE_CLIENT_IGNORE_SSL_ERRORS`), hardcoded third-party API keys (Google Maps, reCAPTCHA Enterprise, Custom Search), and business action endpoints (`/svc/v1/cleverbridge/surl`, `/svc/v1/marketing/forms/leads`, `/api/finance/licenses`).
- **Steps:**
  1. `curl -I https://academy.acronis.com/dist/site-client/assets/app-BOvFy2C8.js.map` → 200, `Content-Type: application/json`.
  2. `curl -s …/app-BOvFy2C8.js.map | jq '.sourcesContent | length'` → 43.
  3. `curl -s …/app-BOvFy2C8.js.map | jq -r '.sourcesContent[0]'` → readable original TypeScript.
  4. Repeat for `c-core-essentials-…js.map` and `c-vendor-common-…js.map`.
- **Impact:** Information disclosure. Reduces cost of every other attack (gives attacker source-level view of business logic, env-var naming convention, hardcoded keys, payment flow paths). The Google API keys embedded in `api-keys.ts` should additionally be confirmed as referrer-restricted; an unrestricted key would allow billable third-party usage against the Acronis project.
- **Remediation:** Disable source map generation in production builds, or generate maps only on a separate internal URL behind auth/VPN, and ensure `sourcesContent` is stripped. Verify Google Cloud API key restrictions (HTTP referrer) and consider rotating the exposed keys.

### 4.4 Discarded / Deprioritized

| Item | Why deprioritized |
| --- | --- |
| Generic GraphQL hits (`query`, `mutation`, `subscription` keywords) | The parser matched **22 generic terms**, not specific GraphQL operations. No actual `gql\`...\`` or `apollo` operation strings were found. Likely false positive from minified vendor bundles. |
| `JWT` regex hits | Zero matches in 292 saved files. |
| `AWS` access key regex hits | Zero matches. |
| `Authorization:` header (raw) | Found in `site-header.js`, but in minified context only (one literal `"Authorization: "` near a comment). No real token. Treat as informational. |
| `oauth_state` matches | All in minified `nonce="` / `state="` boilerplate in third-party widget code. Not a finding. |
| `subscription`, `coupon`, `payment` business keywords | Confirmed present in `app-BOvFy2C8.js` source map. Real business actions, but the **endpoint surfaces** are already covered by hypotheses #2–#6, so the keyword hits alone are not new evidence. |
| `connect.acronis.com` partner portal patterns | 15 JS URLs discovered but the bundles are mostly vendor (react, react-intl, react-router-redux). Real partner-portal logic is behind login; we have no test accounts, so it is a "needs dynamic validation" follow-up, not a triage candidate today. |
| `care.acronis.com` Salesforce aura JS | Salesforce-internal, third-party-ish. Out of scope for active testing. |
| `promo.acronis.com` stripmkt | Marketo strip + cookie; not a finding. |
| Wayback CDX coverage | 429-rate-limited; we relied on katana. Re-attempting with a single UA and longer cooldown is a low-cost follow-up to expand URL coverage. |

---

## 5. Open Questions / Follow-ups

1. **Resolve the base URLs** for the product API and service API. They live behind `HEAD_SITE_MAIN_PUBLIC_BASE_URL_PRODUCT_API_*` and `HEAD_SITE_MAIN_PUBLIC_BASE_URL_*`. Inspect a SSR-rendered page (`view-source:https://academy.acronis.com/...`) to find the pre-rendered `window.__NUXT__` or head env block. This will turn hypotheses #2–#6 into actionable URLs.
2. **Decode `site-header.D22XXGnV.js.map` fully** to find the actual meaning of the 53 `/admin`, `/internal`, `/debug` hits (hypothesis #9).
3. **Cookie / `Set-Cookie` inspection** on `*.acronis.com` to confirm `SameSite` policy and CSRF posture (hypothesis #4). Requires a fresh unauthenticated curl.
4. **Authenticated testing of the Academy endpoints** with user-provided test accounts. Hypotheses #2, #3, #5, #6, #10 all need this.
5. **Verify Google API key restrictions** (hypothesis #7) by calling the keys from a non-Acronis host.
6. **Re-attempt Wayback CDX** with a single non-Safari UA and a longer cooldown, to broaden archived URL coverage.

## 6. Artifacts Produced (all under `work/`)

- `work/seeds.txt` – seed URLs for katana
- `work/katana_urls.txt` – 291,053 raw crawled URLs (incl. 8,787 JS hits)
- `work/js_urls_raw.txt` – 130 unique JS URLs extracted from katana
- `work/js_urls.txt` – 117 in-scope `*.acronis.com` JS URLs
- `work/js_urls_short.txt` – 106 URLs fed to the parser (long SFDC URLs excluded)
- `work/subfinder_acronis.txt` – 100 enumerated subdomains
- `work/cdx_js.json` – Wayback CDX attempt (note: 429, see §1.3)
- `work/parser.json` – 22 MB JSON output of `js_extract.py` (fetches, source maps, summary)
- `work/parser_err.log` – parser stderr (empty for the 106-URL pass)
- `work/js_fetched/` – 292 saved JS / source-map files
- `work/js_report.md` – this report
