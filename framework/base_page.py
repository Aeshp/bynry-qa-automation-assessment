from playwright.sync_api import Page, expect


class BasePage:
    """Shared behavior for all page objects — timeouts, nav, common waits."""

    DEFAULT_TIMEOUT = 15000

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def goto(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")

    def wait_for_element(self, selector: str, timeout: int = None):
        locator = self.page.locator(selector)
        expect(locator).to_be_visible(timeout=timeout or self.DEFAULT_TIMEOUT)
        return locator
