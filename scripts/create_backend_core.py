import os

backend_config = """from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "THERMALIS-X"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "thermalis-dev-secret-key-change-in-production-sha256-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    DATABASE_URL: str = "sqlite:///./thermalis.db"

    # External APIs
    FIRMS_BASE_URL: str = "https://firms.modaps.eosdis.nasa.gov/api"
    FIRMS_MAP_KEY: str = "SAMPLE_FIRMS_MAP_KEY"
    FIRMS_CACHE_TTL_SECONDS: int = 3600
    WEATHER_BASE_URL: str = "https://api.open-meteo.com/v1"
    STAC_API_URL: str = "https://earth-search.aws.element84.com/v1"
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"

    # Event & Spatiotemporal Parameters
    SPATIAL_CLUSTER_RADIUS_KM: float = 1.25
    TEMPORAL_WINDOW_HOURS: float = 24.0
    BASELINE_WINDOW_DAYS: int = 180
    ALERT_COOLDOWN_MINUTES: int = 60
    UNCERTAINTY_THRESHOLD_ENTROPY: float = 0.60
    UNCERTAINTY_THRESHOLD_MARGIN: float = 0.15

    # Modes
    DEMO_MODE: bool = True
    REAL_DATA_MODE: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
"""

with open("backend/app/config.py", "w", encoding="utf-8") as f:
    f.write(backend_config)

error_codes = """from enum import Enum

class ErrorCode(str, Enum):
    # FIRMS Ingestion
    FIRMS_AUTH_FAILED = "FIRMS_001"
    FIRMS_RATE_LIMIT = "FIRMS_002"
    FIRMS_MALFORMED_PAYLOAD = "FIRMS_003"
    FIRMS_SENSOR_UNAVAILABLE = "FIRMS_004"
    FIRMS_INVALID_COORDINATES = "FIRMS_005"

    # Satellite Evidence
    SAT_NO_SCENE = "SAT_001"
    SAT_CLOUD_OBSCURED = "SAT_002"
    SAT_STAC_TIMEOUT = "SAT_003"
    SAT_BAND_DOWNLOAD_FAILED = "SAT_004"

    # Facility Context
    FACILITY_NOT_FOUND = "FACILITY_001"
    FACILITY_BASELINE_INSUFFICIENT = "FACILITY_002"
    OSM_QUERY_FAILED = "FACILITY_003"

    # ML & Classification
    MODEL_NOT_LOADED = "MODEL_001"
    MODEL_INFERENCE_FAILED = "MODEL_002"
    FEATURE_COMPUTATION_FAILED = "MODEL_003"
    MODEL_ABSTAINED = "MODEL_004"

    # Database & System
    DATABASE_UNAVAILABLE = "SYS_001"
    AUTH_UNAUTHORIZED = "AUTH_001"
    AUTH_FORBIDDEN = "AUTH_002"
    RESOURCE_NOT_FOUND = "SYS_002"
    VALIDATION_ERROR = "SYS_003"
"""

with open("backend/app/core/error_codes.py", "w", encoding="utf-8") as f:
    f.write(error_codes)

exceptions = """from typing import Optional, Any, Dict
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
"""

with open("backend/app/core/exceptions.py", "w", encoding="utf-8") as f:
    f.write(exceptions)

logging_py = """import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno
        }
        if hasattr(record, "request_id"):
            log_entry["request_id"] = getattr(record, "request_id")
        if hasattr(record, "event_id"):
            log_entry["event_id"] = getattr(record, "event_id")
        if hasattr(record, "error_code"):
            log_entry["error_code"] = getattr(record, "error_code")
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def setup_logger(name: str = "thermalis") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger("thermalis")
"""

with open("backend/app/core/logging.py", "w", encoding="utf-8") as f:
    f.write(logging_py)

security_py = """from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from backend.app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
"""

with open("backend/app/core/security.py", "w", encoding="utf-8") as f:
    f.write(security_py)

auth_py = """from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from backend.app.core.security import decode_access_token
from backend.app.core.error_codes import ErrorCode

security = HTTPBearer(auto_error=False)

ROLE_PERMISSIONS = {
    "VIEWER": ["read:events", "read:facilities", "read:alerts", "read:analytics"],
    "ANALYST": ["read:events", "read:facilities", "read:alerts", "read:analytics", "write:feedback", "task:satellite"],
    "SUPERVISOR": ["read:events", "read:facilities", "read:alerts", "read:analytics", "write:feedback", "task:satellite", "write:alerts", "admin:model_approve"],
    "ADMIN": ["*"]
}

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        # Default guest/viewer role for demo transparency
        return {"sub": "guest_analyst", "role": "ANALYST", "email": "analyst@thermalis.internal"}
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.AUTH_UNAUTHORIZED, "message": "Invalid or expired authorization token"}
        )
    return payload

def require_role(min_role: str):
    role_hierarchy = {"VIEWER": 1, "ANALYST": 2, "SUPERVISOR": 3, "ADMIN": 4}
    async def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role", "VIEWER")
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(min_role, 1):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": ErrorCode.AUTH_FORBIDDEN, "message": f"Operation requires {min_role} role"}
            )
        return user
    return role_checker
"""

with open("backend/app/core/auth.py", "w", encoding="utf-8") as f:
    f.write(auth_py)

print("Core security, logging, error codes, and config written successfully.")
