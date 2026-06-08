"""
测试认证 API
"""
import pytest


class TestAuth:
    """认证相关测试"""

    def test_login_success(self, client):
        """登录成功"""
        response = client.post("/api/v1/auth/login", json={
            "user_id": "user_001",
            "role": "teacher",
            "name": "张老师"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["user_id"] == "user_001"
        assert data["user"]["role"] == "teacher"
        assert data["expires_in"] == 24 * 3600

    def test_login_invalid_role(self, client):
        """无效 role"""
        response = client.post("/api/v1/auth/login", json={
            "user_id": "user_001",
            "role": "hacker"  # 非法
        })
        assert response.status_code == 422

    def test_get_me_unauthorized(self, client):
        """未认证访问"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code in (401, 403)

    def test_get_me_with_token(self, client, auth_headers):
        """带 token 访问"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_001"
        assert data["role"] == "teacher"

    def test_get_me_with_parent_token(self, client, parent_token):
        """家长 token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "parent"

    def test_refresh_token(self, client, auth_token):
        """刷新 token"""
        response = client.post("/api/v1/auth/refresh", json={
            "token": auth_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["user_id"] == "test_user_001"
