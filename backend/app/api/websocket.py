"""
WebSocket 端点

支持实时双向通信：
  - 客户端订阅 Agent 进度
  - 客户端发送问题 / 反馈
  - 服务端推送状态 / 中间结果
"""
import json
import asyncio
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)

    def disconnect(self, client_id: str, websocket: WebSocket):
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_personal(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            for ws in list(self.active_connections[client_id]):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(client_id, ws)

    async def broadcast(self, message: dict):
        for client_id, connections in self.active_connections.items():
            for ws in list(connections):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(client_id, ws)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket 端点

    消息格式：
    {
      "type": "subscribe" | "command" | "feedback" | "ping",
      "payload": {...}
    }
    """
    await manager.connect(client_id, websocket)

    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "已连接到 Education Services"
        })

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                continue

            msg_type = msg.get("type")
            payload = msg.get("payload", {})

            if msg_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": payload.get("timestamp")})

            elif msg_type == "command":
                # 处理命令（如 /lesson-plan）
                command = payload.get("command")
                args = payload.get("args", [])

                # 模拟处理流程
                await websocket.send_json({
                    "type": "ack",
                    "command": command,
                    "args": args,
                    "message": f"已收到命令：{command}"
                })

                # 模拟进度推送
                for stage in ["locate", "curriculum_map", "pedagogy", "assessment", "complete"]:
                    await asyncio.sleep(0.5)
                    await websocket.send_json({
                        "type": "progress",
                        "stage": stage,
                        "command": command,
                    })

                await websocket.send_json({
                    "type": "result",
                    "command": command,
                    "output_url": f"/api/v1/agents/outputs/{command.replace('/', '')}_{client_id}",
                })

            elif msg_type == "subscribe":
                # 订阅事件
                topic = payload.get("topic", "default")
                await websocket.send_json({
                    "type": "subscribed",
                    "topic": topic,
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id, websocket)


# 启动时的全局事件发送
async def send_event_to_client(client_id: str, event_type: str, data: dict):
    """从其他地方向 WebSocket 客户端发送事件"""
    await manager.send_personal(client_id, {
        "type": event_type,
        "data": data,
    })
