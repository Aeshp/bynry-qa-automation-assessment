# Part 1: Debugging Flaky Test Code

## Identify Flakiness Issues & Root Causes

1. **Synchronous assertions on asynchronous actions.** The original uses plain `assert` immediately after `page.click()`. The DOM hasn't necessarily updated by the time the assertion runs Playwright's `expect()` auto-retries against a condition until it's true or times out, so this alone accounts for a large share of the pass/fail inconsistency.  
2. **Dynamic dashboard loading.** The prompt confirms dashboard elements load asynchronously. A fixed-instant check on `.welcome-message` will race the render. This is worse under CI because headless browsers, shared CI runners, and variable CPU/network conditions all slow down render timing versus a local dev machine the same test that "always passes" locally becomes intermittent the moment it's under CI resource contention.  
3. **`.all()` called before content loads (false-positive bug).** `page.locator(".project-card").all()` called immediately after login can return an empty list if cards haven't rendered yet. An empty list means the `for` loop body never executes, so the tenant-isolation assertion silently never runs the test reports green even when nothing was actually verified. This is a correctness bug, not just a flakiness bug: it can mask a real tenant-isolation failure.  
4. **2FA not handled at all.** The prompt states 2FA applies to *some* users. The original code assumes login always goes straight to `/dashboard`. Any user actually challenged with 2FA causes the URL/element assertions to fail outright, not intermittently this is a full failure mode the original test doesn't account for.  
5. **Manual browser lifecycle management.** Launching `p.chromium.launch()` per test and closing manually means any assertion failure before `browser.close()` leaks the browser process. Across a CI matrix run many times a day, this compounds into resource exhaustion and secondary failures unrelated to the actual test logic.  
6. **Different tenant load times not modeled.** The prompt notes different tenants have different loading characteristics. A single fixed timeout constant applied uniformly is a simplification it works in the fix below by being generous (15s), but a more mature version would key expected load time per tenant/environment rather than treating all tenants identically.  
7. **No cross-browser/viewport handling.** CI runs Chrome, Firefox, Safari (via WebKit) at potentially different screen sizes. The original test never pins a viewport or runs against more than one engine, so layout-dependent selectors or responsive behavior differences between browsers go untested until they break in CI specifically.  
8. **Hardcoded credentials in test code.** Beyond flakiness, `admin@company1.com` / `password123` embedded directly in the test file is bad practice for credential hygiene and makes multi-tenant/multi-user test expansion harder to scale.

***

# Part 2: Test Framework Design

## 1. Framework Structure

```text
workflowpro-qa-automation/
├── pytest.ini
├── requirements.txt
├── conftest.py
├── README.md
├── .env.example
├── config/
│   ├── environments.yaml       # tenant → base_url/api_url/tenant_id/expected_load_ms
│   ├── browserstack.yaml       # BrowserStack capabilities per device/OS
│   └── test_users.yaml         # role/tenant → env var names for credentials
├── framework/
│   ├── config_loader.py        # single source of truth, loads YAML + resolves env vars
│   ├── driver_factory.py       # local Playwright browsers + BrowserStack capability builder
│   ├── api_client.py           # shared API session, handles auth + tenant headers
│   ├── base_page.py            # shared page-object behavior (nav, waits, timeouts)
│   └── auth_helper.py          # login/2FA/token-mint helpers reused across UI + integration tests
├── pages/
│   ├── login_page.py           # Page Object Model — one file per app page
│   ├── dashboard_page.py
│   └── project_page.py
├── tests/
│   ├── ui/                     # browser-driven tests
│   ├── api/                    # pytest + requests, no browser, fast and independent
│   ├── mobile/                 # BrowserStack-driven
│   └── integration/            # combines API + UI + mobile (Part 3)
├── test_data/
│   ├── fixtures.py
│   └── project_payloads.json   # versioned separately from test logic
├── reports/                    # generated HTML reports, traces, screenshots, videos
└── .github/workflows/ci.yml    # CI matrix across browsers
```

### Base classes / core abstractions:
* **BasePage** — every page object inherits this; centralizes navigation, explicit waits, and a default timeout so no test hand-rolls its own wait logic.
* **WorkFlowProAPIClient** — wraps requests.Session, injects Authorization and X-Tenant-ID headers once, reused by both pure API tests and integration tests that seed data before UI checks.
* **config_loader.py** — the only place that reads YAML/env vars; both UI and API layers pull config through this, so there's one source of truth instead of scattered hardcoded values.

## 2. Configuration Management

* **Environments:** environments.yaml maps each tenant (company1, company2, ...) to its base_url, api_url, tenant_id, and a tenant-specific expected_load_ms. Adding a new tenant is a YAML entry, not a code change. The per-tenant load time directly addresses the "different tenants have different loading times" requirement, instead of one blanket timeout applied everywhere.
* **Browsers:** driven via pytest-playwright's --browser CLI flag, matrixed in CI across chromium/firefox/webkit as separate parallel jobs. Viewport sizes are set explicitly in conftest.py rather than relying on CI runner defaults, since default resolutions vary across runners and can silently change layout-dependent test outcomes.
* **Mobile/BrowserStack:** capabilities (device, OS version, real vs virtual device) live in browserstack.yaml, kept separate from web browser config since mobile sessions are provisioned differently (BrowserStack hub vs local Playwright launch).
* **Test data / credentials:** test_users.yaml maps role + tenant to environment variable names, never raw credentials. Actual secret values live in CI secrets (GitHub Actions secrets) or a local .env file that's gitignored — the repo itself never contains a working credential.
* **API payloads:** stored as JSON under test_data/, versioned independently from test logic, so changing test data doesn't require touching test code.

## 3. Design Rationale

* **Page Object Model (pages/) + BasePage** keeps selectors out of test logic. When the UI changes, one page-object file changes, not every test that touches that page.
* **Config-driven tenants** mean scaling to company3, company4, etc. is a data change, not a framework change.
* **Role-based user fixtures** mean Admin/Manager/Employee are data, not separate test files — permission tests parametrize over the same dict instead of duplicating test bodies per role.
* **Separate api_client.py** means API tests never spin up a browser, so they run fast and independently in CI; the same client gets reused inside Part 3's integration tests to seed data before UI assertions run against it.
* **BrowserStack isolated to driver_factory.py** — important caveat: raw Playwright cannot drive native iOS/Android apps. Mobile web (Safari on iOS, Chrome on Android) can go through Playwright + BrowserStack's WebDriver hub; a native app would need Appium via BrowserStack's App Automate instead. I'm flagging this as an open question below rather than assuming which one applies.
* **Env vars over config files for secrets** — credentials never touch the repo; CI injects via secrets, local dev uses .env.
* **Reporting** — pytest-html for a shareable local/CI report, plus Playwright's built-in trace/video/screenshot-on-failure so CI failures are debuggable without needing to reproduce locally.
* **Parallelism** — pytest-xdist splits tests across workers; tenant fixtures parametrize automatically so both tenants get covered without hand-duplicating every test.

## 4. Missing Requirements — Questions I'd Ask Before Building This for Real

* **Test data lifecycle:** Do we get a dedicated seeded test tenant/sandbox per run, or do tests create-and-clean-up against a shared staging environment? Shared state is a major source of cross-test flakiness in CI, especially with parallel workers hitting the same tenant.
* **Mobile app type:** Is the mobile app native iOS/Android, hybrid (React Native/Flutter), or mobile web? This changes the entire toolchain — Appium/BrowserStack App Automate vs Playwright mobile emulation.
* **BrowserStack budget/parallel session limits:** How many concurrent BrowserStack sessions does the plan allow? This dictates how aggressively the cross-browser/mobile matrix can parallelize in CI without queueing delays.
* **Auth for automation:** Is there a dedicated API-based login/token-mint flow for tests (bypassing UI login + 2FA entirely for setup), or must every test go through full UI login? UI-only login makes the API+integration tests in Part 3 significantly slower.
* **Reporting destination:** Does this need to integrate with an existing dashboard (Allure, TestRail, Slack notifications), or is a standalone HTML report per CI run sufficient?
* **Test environment stability:** Is staging a stable, dedicated QA environment, or does it get redeployed/reset on a schedule that could wipe test data mid-run?
* **Role permission matrix:** Is there a documented list of exactly what each role (Admin/Manager/Employee) can and cannot see/do? Without this, permission tests are guesswork rather than verification against a spec.
* **Retry policy:** Should genuinely non-deterministic failures auto-retry once in CI (pytest-rerunfailures), or should every failure be investigated manually with zero tolerance for retries masking real bugs?
