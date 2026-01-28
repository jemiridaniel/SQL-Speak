# api/dependencies.py

from functools import lru_cache
from pathlib import Path
from typing import Dict

import tomli as tomllib  # for Python 3.8
from fastapi import Header
from pydantic import BaseModel

from core.models import UserContext
from .auth import get_current_user as get_user_context

CONFIG_PATH = Path("config/local.toml")


class AppConfig(BaseModel):
    data_sources: Dict[str, str]


@lru_cache
def get_config() -> AppConfig:
    with CONFIG_PATH.open("rb") as f:
        raw = tomllib.load(f)

    ds = raw.get("data_sources", {})
    return AppConfig(data_sources=ds)


def get_user_context(x_user_id: str = Header("local-dev"), x_user_name: str = Header("Local Developer")) -> UserContext:
    """
    Temporary identity model:
    - X-User-Id: stable user identifier (e.g., email or UUID)
    - X-User-Name: display name
    Later, these will come from Azure AD tokens instead.
    """
    return UserContext(
        id=x_user_id,
        display_name=x_user_name,
        roles=["admin"],
    )
