import os
from typing import Any, Optional


def get_env(env_var: str, default: Any):
    value = os.getenv(env_var)

    return value if value is not None else default


def get_required_env(env_var: str, error_message: Optional[str] = None) -> str:
    """
    Get a required environment variable or raise a ValueError if it's not set.

    Args:
        env_var: The name of the environment variable
        error_message: Custom error message (optional)

    Returns:
        The value of the environment variable

    Raises:
        ValueError: If the environment variable is not set or empty
    """
    value = os.getenv(env_var)
    if not value or not value.strip():
        if error_message:
            raise ValueError(error_message)
        raise ValueError(f"{env_var} environment variable not set")

    return value.strip()
