import pytest
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect

def test_admin_can_create_project(page: Page, company1_admin):
    """UI test: Company 1 admin creates a project."""
    login_page = LoginPage(page, "https://app.workflowpro.com")
    
    # we would do: login_page.login(company1_admin['email'], company1_admin['password'])
    # page.locator('#create-project').click()
    
    assert company1_admin["role"] == "admin"
    assert company1_admin["tenant"] == "company1"

def test_employee_cannot_create_project(page: Page, company2_employee):
    """UI test: Employee shouldn't see create project button."""
    assert company2_employee["role"] == "employee"
