## QA Automation Case Study: WorkflowPro

A QA automation case study for a B2B SaaS platform — built for QA Automation Engineering.


## Tech Stack
- pytest
- pytest-playwright
- playwright
- pytest-html
- pytest-xdist
- requests
- pyyaml
- python-dotenv

## Environment Setup
Choose one of the following setup options:

### Option A — Conda (Recommended)
```bash
conda create -n workflowpro-qa python=3.11
conda activate workflowpro-qa
pip install -r requirements.txt
playwright install --with-deps
```

### Option B — venv
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install --with-deps
```

### Option C — No virtual environment
```bash
pip install -r requirements.txt
playwright install --with-deps
```

## Environment Variables
Credentials are never hardcoded. Create a `.env` file in the root directory (you can copy the existing `.env.example` to `.env`) and populate the following variables used by the framework:
- `TEST_C1_ADMIN_EMAIL`
- `TEST_C1_ADMIN_PASSWORD`
- `TEST_C1_MANAGER_EMAIL`
- `TEST_C1_MANAGER_PASSWORD`
- `TEST_C2_EMPLOYEE_EMAIL`
- `TEST_C2_EMPLOYEE_PASSWORD`
- `TEST_API_TOKEN`

## Running Tests
Run tests using `pytest` (configured in `pytest.ini` to auto-generate HTML reports, screenshots, videos, and traces on failure):

- **Run full suite:**
  `pytest tests/`
- **Run a single part by actual folder path:**
  `pytest tests/ui/`
  `pytest tests/api/`
  `pytest tests/integration/`
- **Run cross-browser (Playwright matrix):**
  `pytest tests/ --browser chromium --browser firefox --browser webkit`
- **Run in parallel:**
  `pytest tests/ -n auto`
- **Run with HTML report generation:**
  `pytest tests/ --html=reports/report.html --self-contained-html` (Note: This is automatically appended by `pytest.ini` default flags)

## Project Structure

```text
bynry-qa-automation-assessment/
├── CASE_STUDY_REPORT.md (Design rationale and technical architecture)
├── README.md (Project setup, tech stack, and execution guide)
├── TEST_PLAN.md (Detailed test scope and execution strategy)
├── pytest.ini (Pytest CLI defaults and custom markers)
├── requirements.txt (Python package dependencies and versions)
├── .env.example (Template for local environment credentials)
├── config/
│   ├── environments.yaml (Tenant base URLs and expected load times)
│   └── test_users.yaml (Maps roles and tenants to environment variables)
├── framework/
│   ├── api_client.py (Shared requests session with tenant headers)
│   ├── base_page.py (Shared page object behavior and common waits)
│   ├── config_loader.py (Loads YAML configurations and environment variables)
│   └── driver_factory.py (Browser setup and BrowserStack capability builder)
├── pages/
│   └── login_page.py (Page object handling UI login and OTP)
├── reports/
│   └── (Generated HTML reports)
└── tests/
    ├── api/
    │   └── test_projects_api.py (Validates API client tenant and authorization headers)
    ├── integration/
    │   └── test_project_flow.py (End-to-end API seeding and UI validation)
    ├── mobile/
    │   └── test_mobile_dashboard.py (Validates mobile layout via viewport dimensions)
    └── ui/
        ├── test_login.py (Login/tenant isolation logic; two tests marked skip — see TEST_PLAN.md)
        └── test_project_creation.py (Validates RBAC fixture injection for projects)
```

## Reports & Artifacts
Test reports are automatically saved in the `reports/` directory. To view a report, open the `.html` file in any web browser. Video recordings and traces are retained on failure (configured in `pytest.ini`).

This repository includes three primary execution reports to demonstrate the development lifecycle:
*   **`ui_login_execution_report.html`**: Targeted UI debugging run (Part 1). Contains 5 tests demonstrating intentional Playwright timeouts and asynchronous DOM state failures.
*   **`integration_flow_report.html`**: Isolated E2E run (Part 3). Contains 1 complete cross-platform test validating API seeding, UI visualization, mobile responsiveness, and strict tenant isolation.
*   **`full_suite_execution_report.html`**: The final CI pipeline validation. Contains the complete test matrix (11 active, 2 skipped), proving the entire framework executes flawlessly together.

## Design Rationale
For comprehensive design rationale, technical decisions, and architecture assumptions, please refer to [CASE_STUDY_REPORT.md](CASE_STUDY_REPORT.md).