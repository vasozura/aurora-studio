"""Controlled Aurora error types."""


class AuroraError(Exception):
    """Base error for Aurora Studio."""


class ValidationError(AuroraError):
    """Raised when validation fails."""


class OwnershipError(AuroraError):
    """Raised when a module ownership boundary is violated."""


class UnsupportedOperationError(AuroraError):
    """Raised when an operation is unsupported by the current skeleton."""


class NotReadyError(AuroraError):
    """Raised when a requested operation is not ready for implementation."""
