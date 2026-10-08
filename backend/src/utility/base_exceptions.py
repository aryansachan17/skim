from http import HTTPStatus


class BaseHTTPError(Exception):
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    code: str = "INTERNAL_ERROR"
    default_message: str = "Something went wrong. Please try again."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class BadRequestError(BaseHTTPError):
    status_code = HTTPStatus.BAD_REQUEST
    code = "BAD_REQUEST"
    default_message = "The request was invalid."


class UnauthenticatedError(BaseHTTPError):
    status_code = HTTPStatus.UNAUTHORIZED
    code = "UNAUTHENTICATED"
    default_message = "Please log in to continue."


class NotFoundError(BaseHTTPError):
    status_code = HTTPStatus.NOT_FOUND
    code = "NOT_FOUND"
    default_message = "The requested resource was not found."


class ConflictError(BaseHTTPError):
    status_code = HTTPStatus.CONFLICT
    code = "CONFLICT"
    default_message = "This resource already exists."


class ServiceUnavailableError(BaseHTTPError):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    code = "SERVICE_UNAVAILABLE"
    default_message = "A dependency is unavailable. Please try again shortly."
