import os
import yaml
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path(__file__).parent.parent / "config"


@lru_cache
def load_environments() -> dict:
    with open(CONFIG_DIR / "environments.yaml") as f:
        return yaml.safe_load(f)


@lru_cache
def load_users() -> dict:
    with open(CONFIG_DIR / "test_users.yaml") as f:
        return yaml.safe_load(f)["users"]


def get_env_config(tenant: str) -> dict:
    envs = load_environments()["environments"]
    if tenant not in envs:
        raise ValueError(f"Unknown tenant '{tenant}'. Available: {list(envs.keys())}")
    return envs[tenant]


def get_user_credentials(user_key: str) -> dict:
    users = load_users()
    if user_key not in users:
        raise ValueError(f"Unknown test user '{user_key}'. Available: {list(users.keys())}")
    user = users[user_key]
    email = os.getenv(user["email_env"])
    password = os.getenv(user["password_env"])
    if not email or not password:
        raise EnvironmentError(
            f"Missing env vars {user['email_env']}/{user['password_env']} for '{user_key}'"
        )
    return {"email": email, "password": password, "role": user["role"], "tenant": user["tenant"]}
