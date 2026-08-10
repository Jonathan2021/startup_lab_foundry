"""Expected application-level errors."""


class StartupFoundryError(Exception):
    """Base class for expected, user-facing application errors."""


class ConfigurationError(StartupFoundryError):
    """Raised when application configuration is invalid."""


class VentureNotFoundError(StartupFoundryError):
    """Raised when a requested venture does not exist."""

    def __init__(self, venture_id: str) -> None:
        super().__init__(f"Venture {venture_id!r} was not found.")


class ValidationError(StartupFoundryError):
    """Raised when command input violates an application invariant."""


class ConflictError(StartupFoundryError):
    """Raised when a command would overwrite existing semantic history."""


class ReferenceError(StartupFoundryError):
    """Raised when a referenced record is missing or belongs elsewhere."""
