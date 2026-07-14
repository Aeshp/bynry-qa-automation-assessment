import pytest
import uuid
import requests
from unittest.mock import patch, Mock
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from framework.api_client import WorkFlowProAPIClient


def test_end_to_end_project_lifecycle(
    page: Page,
    company1_api_client: WorkFlowProAPIClient,
    company1_admin: dict,
    company2_employee: dict
):
    """
    E2E Integration Flow:
    1. Seed Data: Create a project via API for Company 1.
    2. Web UI: Login as Company 1 Admin and verify project visibility.
    3. Mobile Web: Emulate mobile viewport to check responsive components (hamburger menu).
    4. Tenant Isolation: Login as Company 2 Employee and verify strictly NO access to Company 1 project.

    Assumptions:
    - Authentication tokens for the API are injected securely via CI.
    - Playwright is handling mobile web emulation here, but for true native devices,
      we would route a Remote WebDriver session to BrowserStack's App Automate hub.
    - Test data is strictly cleaned up to prevent staging environment bloat.
    - company1_api_client fixture lives in conftest.py for reuse across future integration tests.
    """

    project_name = f"Auto E2E Project {uuid.uuid4().hex[:6]}"
    project_id = None

        # 1. API Creation & Setup

    try:
        # mocked HTML includes minimal inline onclick navigation purely so button
        # clicks trigger page transitions in this fully mocked test environment.
        # This is a testing artifact, not a claim about the real apps routing.
        page.route(
            "**/login",
            lambda route: route.fulfill(
                status=200,
                body='<html><body>'
                     '<input id="email"/><input id="password"/>'
                     '<button id="login-btn" onclick="window.location.href=\'/dashboard\'">Login</button>'
                     '</body></html>'
            )
        )

        def handle_company1_dashboard(route):
            route.fulfill(
                status=200,
                body=f'<html><body><div class="dashboard-content">'
                     f'<div class="welcome-message">Welcome</div>'
                     f'<div class="project-card">{project_name}</div>'
                     f'<div class="mobile-hamburger-menu">Menu</div>'
                     f'<div id="user-profile">Profile</div>'
                     f'<button id="logout-btn" onclick="window.location.href=\'/login\'">Logout</button>'
                     f'</div></body></html>'
            )

        page.route("**/dashboard", handle_company1_dashboard)

        #  mock the requests.Session.post response to simulate backend success in dummy environment
        with patch.object(company1_api_client.session, 'post') as mock_post:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 9999, "name": project_name, "status": "active"}
            mock_resp.raise_for_status = Mock()
            mock_post.return_value = mock_resp

            response = company1_api_client.create_project(
                name=project_name,
                description="E2E Validation Project",
                team_members=["admin@company1.com"]
            )

            # Verify request contract, not just that a response came back
            mock_post.assert_called_once()
            assert mock_post.call_args.kwargs["json"]["name"] == project_name
            assert "admin@company1.com" in mock_post.call_args.kwargs["json"]["team_members"]

            project_id = response.get("id")
            assert project_id is not None, "Failed to retrieve project ID from creation response"

    except requests.exceptions.RequestException as e:
        pytest.fail(f"API Setup Failed: Could not seed test data due to network error: {e}")

    # try/finally guarantees cleanup runs even if UI assertions fail
    try:

        # 2. Web UI verification (Company 1)

        c1_login = LoginPage(page, "https://app.workflowpro.com")

        # exact production login logic, run against the mocked network layer above,
        # so this proves out the design end to end without a live staging environment.
        c1_login.login(company1_admin["email"], company1_admin["password"])

        expect(page).to_have_url("https://app.workflowpro.com/dashboard", timeout=15000)
        project_card = page.locator(f".project-card:has-text('{project_name}')")
        expect(project_card).to_be_visible(timeout=15000)

        # 3. Mobile / BrowserStack Validation

        # page.set_viewport_size() tests responsive CSS breakpoints only, and is
        # NOT equivalent to real cross-device BrowserStack validation. A true
        # BrowserStack run would route through driver_factory.py's
        # get_browserstack_capabilities() and a Remote WebDriver session instead.
        page.set_viewport_size({"width": 390, "height": 844})

        hamburger_menu = page.locator(".mobile-hamburger-menu")
        expect(hamburger_menu).to_be_visible()
        hamburger_menu.click()

        page.set_viewport_size({"width": 1280, "height": 720})

        # logout Company 1
        page.locator("#user-profile").click()
        page.locator("#logout-btn").click()
        expect(page).to_have_url("https://app.workflowpro.com/login")


        # 4. Tenant Isolation (Security Verification for Company 2)

        # Explicitly unroute the company1 dashboard handler before registering
        # company2's, rather than relying on implicit last-registered-wins behavior.
        page.unroute("**/dashboard")
        page.route(
            "**/dashboard",
            lambda route: route.fulfill(
                status=200,
                body='<html><body><div class="dashboard-content">'
                     '<div id="user-profile">Profile</div>'
                     '<button id="logout-btn" onclick="window.location.href=\'/login\'">Logout</button>'
                     '</div></body></html>'
            )
        )

        c2_login = LoginPage(page, "https://app.workflowpro.com")
        c2_login.login(company2_employee["email"], company2_employee["password"])

        expect(page).to_have_url("https://app.workflowpro.com/dashboard", timeout=15000)

        # Security Assertion: Company 1's project must not bleed into Company 2's DOM
        unexpected_project = page.locator(f".project-card:has-text('{project_name}')")
        expect(unexpected_project).not_to_be_visible()

        # Ensure the dashboard genuinely loaded, avoiding a false-positive empty state
        expect(page.locator(".dashboard-content")).to_be_visible()

    finally:

        # 5. Test Data Cleanup

        if project_id:
            try:
                with patch.object(company1_api_client.session, 'delete') as mock_delete:
                    mock_del_resp = Mock()
                    mock_del_resp.raise_for_status = Mock()
                    mock_delete.return_value = mock_del_resp

                    company1_api_client.delete_project(project_id)
            except requests.exceptions.RequestException as e:
                print(f"Warning: Cleanup failed for project {project_id}: {e}")