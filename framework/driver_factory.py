import os
from playwright.sync_api import sync_playwright

BROWSERSTACK_HUB = "https://hub-cloud.browserstack.com/wd/hub"


def get_playwright_browser(playwright, browser_name: str, headless: bool = True):
    """Local Playwright browser — used for chromium/firefox/webkit in CI matrix."""
    browser_launcher = getattr(playwright, browser_name)
    return browser_launcher.launch(headless=headless)


def get_browserstack_capabilities(device: str, os_version: str, real_mobile: bool = True):
    """
    Capability builder for BrowserStack mobile (iOS/Android) sessions.
    Actual mobile tests run via Appium/BrowserStack SDK, not raw Playwright,
    since Playwright doesn't drive native iOS/Android apps.
    """
    return {
        "bstack:options": {
            "deviceName": device,
            "osVersion": os_version,
            "realMobile": str(real_mobile).lower(),
            "projectName": "WorkFlowPro QA",
            "buildName": os.getenv("CI_BUILD_ID", "local-run"),
            "sessionName": f"{device}-{os_version}",
        }
    }
