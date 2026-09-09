from fastapi import Depends, HTTPException, status
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
