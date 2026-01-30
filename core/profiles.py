from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Profile:
    name: str
    read_only: bool = True
    auto_limit: Optional[int] = 100
    explain: bool = False
    db_type: str = "sqlite"

_PROFILES: Dict[str, Profile] = {
    "sqlite-dev": Profile(
        name="sqlite-dev",
        read_only=False,
        auto_limit=None,
        explain=False,
        db_type="sqlite",
    ),
    "prod-readonly": Profile(
        name="prod-readonly",
        read_only=True,
        auto_limit=100,   # always enforce LIMIT
        explain=False,
        db_type="sqlite",
    ),
    # NEW: benchmark-postgres profile
    "benchmark-postgres": Profile(
        name="benchmark-postgres",
        read_only=False,
        auto_limit=100,
        explain=True,
        db_type="postgres",
    ),
}

def get_profile(name: str) -> Profile:
    try:
        return _PROFILES[name]
    except KeyError:
        raise ValueError(f"Unknown profile: {name}")
