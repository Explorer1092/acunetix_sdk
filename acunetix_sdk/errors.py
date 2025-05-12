# Custom Acunetix API errors 

class AcunetixError(Exception):
    """Base class for Acunetix API errors."""
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self):
        if self.status_code:
            return f"[Status {self.status_code}] {super().__str__()} - Response: {self.response_text or 'N/A'}"
        return super().__str__()

class AuthenticationError(AcunetixError):
    """Error for authentication failures (e.g., 401, 403)."""
    pass

class NotFoundError(AcunetixError):
    """Error when a resource is not found (e.g., 404)."""
    pass

class BadRequestError(AcunetixError):
    """Error for malformed requests (e.g., 400, 422)."""
    pass

class RateLimitError(AcunetixError):
    """Error for rate limiting (e.g., 429)."""
    pass

class ServerError(AcunetixError):
    """Error for server-side issues (e.g., 500, 502, 503, 504)."""
    pass


ERROR_MAP = {
    400: BadRequestError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    409: BadRequestError, # Conflict, often a form of bad request due to state
    422: BadRequestError, # Unprocessable Entity
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}

def raise_for_status(status_code: int, response_text: str):
    """Raise an AcunetixError for a given status code if it's an error status."""
    if status_code in ERROR_MAP:
        error_class = ERROR_MAP[status_code]
        raise error_class(
            message=f"API request failed.",
            status_code=status_code,
            response_text=response_text
        )
    if 400 <= status_code < 500:
        raise BadRequestError(
            message=f"Client error.",
            status_code=status_code,
            response_text=response_text
        )
    if 500 <= status_code < 600:
        raise ServerError(
            message=f"Server error.",
            status_code=status_code,
            response_text=response_text
        ) 