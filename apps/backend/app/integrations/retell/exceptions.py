class RetellError(Exception):
    """Base exception for Retell errors."""
    pass

class RetellAuthenticationError(RetellError):
    """Raised when Retell authentication fails."""
    pass

class RetellConfigurationError(RetellError):
    """Raised when Retell configuration is missing or invalid."""
    pass

class RetellNetworkError(RetellError):
    """Raised when there is a network error communicating with Retell."""
    pass

class RetellAPIError(RetellError):
    """Raised when the Retell API returns an error response."""
    def __init__(self, message: str, status_code: int, response_data: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
