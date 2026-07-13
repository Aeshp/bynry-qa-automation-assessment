import os
import pytest
from playwright.sync_api import Page, expect

# test data pulled from environment,not hardcoded.
# In CI, these get injected as secrets, locally, use a .env file (not committed).
TEST_USERS = {
    "company1_admin": {
        "email": os.getenv("TEST_C1_ADMIN_EMAIL", "admin@company1.com"),
        "password": os.getenv("TEST_C1_ADMIN_PASSWORD", "password123"),
    },
    "company2_user": {
        "email": os.getenv("TEST_C2_USER_EMAIL", "user@company2.com"),
        "password": os.getenv("TEST_C2_USER_PASSWORD", "password123"),
    },
}


def login(page: Page, email: str, password: str):
    """
    Shared login helper that handles the optional 2FA challenge.
    Not all users are challenged, so we probe for the OTP field with a short
    timeout rather than assuming its presence or absence.
    """
    page.goto("https://app.workflowpro.com/login")
    page.locator("#email").fill(email)
    page.locator("#password").fill(password)
    page.locator("#login-btn").click()

    otp_input = page.locator("#otp-code")
    try:
        expect(otp_input).to_be_visible(timeout=5000)
        otp_code = os.getenv("TEST_OTP_CODE", "000000")  # test-env static OTP or mocked service
        otp_input.fill(otp_code)
        page.locator("#otp-submit-btn").click()
    except AssertionError:
        # no 2FA challenge appeared for this user - proceed as normal.
        pass


def test_user_login_fixed(page: Page):
    creds = TEST_USERS["company1_admin"]
    login(page, creds["email"], creds["password"])

    # web first assertions auto-retry until timeout, no manual sleeps needed
    expect(page).to_have_url("https://app.workflowpro.com/dashboard", timeout=15000)
    expect(page.locator(".welcome-message")).to_be_visible(timeout=15000)


def test_multi_tenant_access_fixed(page: Page):
    creds = TEST_USERS["company2_user"]
    login(page, creds["email"], creds["password"])

    expect(page).to_have_url("https://app.workflowpro.com/dashboard", timeout=15000)

    # wait for at least one card before trusting the collection —
    # prevents the false positive empty list bug from the original test.
    project_cards = page.locator(".project-card")
    expect(project_cards.first).to_be_visible(timeout=15000)

    count = project_cards.count()
    assert count > 0, "Expected at least one project card to load for Company2 user"

    for i in range(count):
        expect(project_cards.nth(i)).to_contain_text("Company2")


@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_login_cross_browser_placeholder(browser_name):
    """
    Documents intent: run the full suite across browsers via
    `pytest --browser chromium --browser firefox --browser webkit`.
    Left as a placeholder since actual cross-browser execution is
    driven by pytest-playwright CLI flags / CI matrix, not in-test logic.
    """
    pass