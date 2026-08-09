"""Application-specific exception hierarchy.

All exceptions here inherit from `AppException`, which carries a
human-readable `message` and an HTTP `status_code`. Business logic layers
(services, clients) raise these freely without knowing about FastAPI or HTTP.
The translation into an actual HTTP response happens only in `app/main.py`.
"""


class AppException(Exception):
    """Base class for all custom application exceptions."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# --- Upload / input validation errors (client's fault -> 4xx) ---


class InvalidFileTypeError(AppException):
    def __init__(self, message: str = "Uploaded file type is not supported.") -> None:
        super().__init__(message=message, status_code=400)


class FileTooLargeError(AppException):
    def __init__(self, message: str = "Uploaded file exceeds the maximum allowed size.") -> None:
        super().__init__(message=message, status_code=413)


class EmptyFileError(AppException):
    def __init__(self, message: str = "Uploaded file is empty.") -> None:
        super().__init__(message=message, status_code=400)


class InvalidImageError(AppException):
    def __init__(self, message: str = "Uploaded file could not be read as a valid image.") -> None:
        super().__init__(message=message, status_code=400)


# --- Model / inference errors (server's fault -> 5xx) ---


class ModelLoadError(AppException):
    def __init__(self, message: str = "Failed to load the object detection model.") -> None:
        super().__init__(message=message, status_code=500)


class InferenceError(AppException):
    def __init__(self, message: str = "Object detection inference failed.") -> None:
        super().__init__(message=message, status_code=500)


# --- Generic resource error ---


class ResourceNotFoundError(AppException):
    def __init__(self, message: str = "The requested resource was not found.") -> None:
        super().__init__(message=message, status_code=404)