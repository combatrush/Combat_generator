class AnimationError(Exception):
    """Base class for animation-related exceptions."""
    pass

class ModelLoadError(AnimationError):
    """Raised when there's an error loading AI models."""
    pass

class RenderError(AnimationError):
    """Raised when there's an error during animation rendering."""
    pass

class ValidationError(AnimationError):
    """Raised when there's an error validating input data."""
    pass

class AuthenticationError(Exception):
    """Raised when there's an authentication error."""
    pass

class AuthorizationError(Exception):
    """Raised when there's an authorization error."""
    pass

class DatabaseError(Exception):
    """Raised when there's a database-related error."""
    pass

class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass

class ResourceNotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass

class APIError(Exception):
    """Base class for API-related errors."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}
