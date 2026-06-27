"""Readiness states for Aurora Studio skeleton."""

from enum import Enum


class Readiness(str, Enum):
    """Specification and implementation readiness states."""

    NOT_READY = "Not Ready"
    READY_FOR_DESIGN = "Ready For Design"
    READY_FOR_IMPLEMENTATION = "Ready For Implementation"
    DEPRECATED = "Deprecated"
