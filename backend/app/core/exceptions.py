"""
STARTWISE AI — Custom Exception Hierarchy
Provides HTTP-mapped exceptions used across the application.
"""

from fastapi import HTTPException, status


class StartwiseBaseException(HTTPException):
    """Base exception for all STARTWISE AI errors."""
    status_code: int = 500
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str = None, message: str = None, error_code: str = None):
        msg = message or detail or self.detail
        self.message = msg
        self.error_code = error_code or "ERROR"
        super().__init__(
            status_code=self.status_code,
            detail=msg,
        )


AppException = StartwiseBaseException


class NotFoundException(StartwiseBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found."


class UnauthorizedException(StartwiseBaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication required."

    def __init__(self, detail: str = None):
        super().__init__(detail=detail or self.detail)
        self.headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenException(StartwiseBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You don't have permission to perform this action."


class EmailNotVerifiedException(StartwiseBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "EMAIL_NOT_VERIFIED"

    def __init__(self, email: str = "", message: str = "Please verify your email before logging in."):
        super().__init__(detail="EMAIL_NOT_VERIFIED", message=message, error_code="EMAIL_NOT_VERIFIED")
        self.email = email



class ConflictException(StartwiseBaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource already exists."


class ValidationException(StartwiseBaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error."


class BadRequestException(StartwiseBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request."


class MLModelException(StartwiseBaseException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "ML model inference failed."


class DatabaseException(StartwiseBaseException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Database operation failed."
