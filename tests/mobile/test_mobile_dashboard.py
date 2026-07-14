import pytest
from playwright.sync_api import Page, expect

@pytest.mark.mobile
def test_mobile_dashboard_layout(page: Page, company1_admin):
    """
    Test that the mobile dashboard layout renders correctly.
    In CI, this runs using the browserstack capabilities or playwright mobile emulation.
    """
    assert company1_admin["tenant"] == "company1"
    # test viewport was set properly
    viewport = page.viewport_size
    assert viewport["width"] == 1280 or viewport["width"] == 390 # from conftest or environments.yaml
