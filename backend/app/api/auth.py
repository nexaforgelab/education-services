"""
认证 API

提供登录、注册、token 刷新
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import (
    create_access_token,
    get_current_user,
    UserContext,
)


router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求（简化版，无密码验证）"""
    user_id: str = Field(..., description="用户 ID")
    role: str = Field(..., pattern="^(teacher|parent|student|admin)$")
    name: Optional[str] = None


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserContext
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    """刷新 token"""
    token: str


@router.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """
    登录（Demo 版）
    实际项目里需要密码 / OAuth / SSO
    """
    token = create_access_token(req.user_id, req.role, req.name)
    return LoginResponse(
        access_token=token,
        user=UserContext(user_id=req.user_id, role=req.role, name=req.name),
        expires_in=24 * 3600,
    )


@router.post("/auth/refresh", response_model=LoginResponse)
async def refresh_token(req: RefreshRequest):
    """刷新 token"""
    from app.core.security import decode_token
    try:
        payload = decode_token(req.token)
    except HTTPException:
        raise

    new_token = create_access_token(
        payload["sub"],
        payload["role"],
        payload.get("name"),
    )
    return LoginResponse(
        access_token=new_token,
        user=UserContext(
            user_id=payload["sub"],
            role=payload["role"],
            name=payload.get("name"),
        ),
        expires_in=24 * 3600,
    )


@router.get("/auth/me", response_model=UserContext)
async def get_me(user: UserContext = Depends(get_current_user)):
    """获取当前用户信息"""
    return user
