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
workflowpro-qa-automation/
├── CASE_STUDY_REPORT.md
├── README.md
├── TEST_PLAN.md
├── pytest.ini
├── requirements.txt
├── .env.example
├── .env
├── config/
│   ├── environments.yaml
│   └── test_users.yaml
├── framework/
│   ├── api_client.py
│   ├── base_page.py
│   ├── config_loader.py
│   └── driver_factory.py
├── pages/
│   └── login_page.py
├── reports/
│   └── (Generated HTML reports)
└── tests/
    ├── api/
    │   └── test_projects_api.py
    ├── integration/
    │   └── test_project_flow.py
    ├── mobile/
    │   └── test_mobile_dashboard.py
    └── ui/
        ├── test_login.py
        └── test_project_creation.py
```

## Reports & Artifacts
Test reports are automatically saved in the `reports/` directory. By default, `pytest` generates `reports/report.html`. To view a report, simply open the `.html` file in any web browser. Video recordings and traces are retained on failure (configured in `pytest.ini`).

## Design Rationale
For comprehensive design rationale, technical decisions, and architecture assumptions, please refer to [CASE_STUDY_REPORT.md](CASE_STUDY_REPORT.md).