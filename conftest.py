import os
import pytest
from framework.config_loader import get_env_config, get_user_credentials
from framework.api_client import WorkFlowProAPIClient


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(params=["company1", "company2"])
def tenant_config(request):
    return get_env_config(request.param)


@pytest.fixture
def api_client(tenant_config):
    token = os.getenv("TEST_API_TOKEN")
    return WorkFlowProAPIClient(
        base_url=tenant_config["api_url"],
        tenant_id=tenant_config["tenant_id"],
        token=token,
    )


def user_fixture(user_key: str):
    @pytest.fixture
    def _fixture():
        return get_user_credentials(user_key)
    return _fixture


company1_admin = user_fixture("company1_admin")
company2_employee = user_fixture("company2_employee")
