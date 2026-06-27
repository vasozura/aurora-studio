"""ID helpers for Aurora Studio skeleton."""

from uuid import uuid4


def new_id(prefix: str) -> str:
    """Return a stable random ID with a human-readable prefix.

    IDs must not depend on prompt text, provider output, GUI state or generated media.
    """

    cleaned = prefix.strip().lower().replace(" ", "-")
    if not cleaned:
        cleaned = "id"
    return f"{cleaned}-{uuid4().hex}"
