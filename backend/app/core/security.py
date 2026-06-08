"""
认证与授权

简化版：JWT 鉴权，role-based access control
"""
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.config import settings


# JWT 配置
JWT_SECRET = settings.anthropic_api_key or "dev-secret-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

bearer_scheme = HTTPBearer()


class UserContext(BaseModel):
    """当前用户上下文"""
    user_id: str
    role: str  # teacher | parent | student | admin
    name: Optional[str] = None


def create_access_token(user_id: str, role: str, name: Optional[str] = None) -> str:
    """生成 JWT token"""
    payload = {
        "sub": user_id,
        "role": role,
        "name": name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserContext:
    """从 JWT token 获取当前用户"""
    payload = decode_token(credentials.credentials)
    return UserContext(
        user_id=payload["sub"],
        role=payload["role"],
        name=payload.get("name"),
    )


def require_role(*allowed_roles: str):
    """角色权限装饰器"""
    async def checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not allowed. Required: {allowed_roles}",
            )
        return user
    return checker
