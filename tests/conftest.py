import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Override default context args.
    ignore_https_errors: staging/tenant subdomains use self-signed certs
    in our test environment, so we relax cert validation here (never in prod config).
    """
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1280, "height": 720},  # explicit, since CI runners
        # default to varying resolutions and this affects element visibility/layout
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Slow down CI-only flake sources: headless mode runs faster than real
    user interaction, sometimes outrunning client-side JS state updates.
    """
    return {
        **browser_type_launch_args,
        "slow_mo": 0,  # keep 0 by default; bump locally only when debugging
    }


def pytest_addoption(parser):
    parser.addini(
        "base_url",
        default="https://app.workflowpro.com",
        help="Base URL for the app under test",
    )