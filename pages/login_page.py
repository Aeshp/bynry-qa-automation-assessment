from framework.base_page import BasePage
from playwright.sync_api import expect


class LoginPage(BasePage):
    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    LOGIN_BTN = "#login-btn"
    OTP_INPUT = "#otp-code"
    OTP_SUBMIT = "#otp-submit-btn"

    def login(self, email: str, password: str, otp_code: str = None):
        self.goto("/login")
        self.page.locator(self.EMAIL_INPUT).fill(email)
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        self.page.locator(self.LOGIN_BTN).click()

        otp_field = self.page.locator(self.OTP_INPUT)
        try:
            expect(otp_field).to_be_visible(timeout=5000)
            otp_field.fill(otp_code or "000000")
            self.page.locator(self.OTP_SUBMIT).click()
        except AssertionError:
            pass  # no 2FA challenge for this user
