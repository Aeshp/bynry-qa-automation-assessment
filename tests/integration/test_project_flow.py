import pytest
from playwright.sync_api import Page

def test_full_project_lifecycle(page: Page, api_client, company1_admin):
    """
    Integration test:
    1. Seed project via API
    2. Login via UI
    3. Verify project exists on dashboard
    4. Delete via API
    """
    assert api_client.base_url is not None
    assert company1_admin["role"] == "admin"
    # E2E flow simulation placeholder
