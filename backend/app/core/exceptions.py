from typing import Optional, Any, Dict
from backend.app.core.error_codes import ErrorCode

class ThermalisException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ResourceNotFoundException(ThermalisException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=f"{resource} with identifier '{identifier}' was not found.",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)}
        )

class ModelInferenceException(ThermalisException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.MODEL_INFERENCE_FAILED,
            message=message,
            status_code=500,
            details=details
        )
