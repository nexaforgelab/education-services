#!/usr/bin/env python3
"""
llm_client.py — 真实 LLM 集成（Anthropic Claude）

提供统一的 LLM 调用接口，支持：
  - Claude Opus 4.7 (主 Agent)
  - Claude Sonnet 4.5 (子 Agent)
  - 流式响应
  - 重试 / 限流

用法:
  from llm_client import LLMClient
  
  client = LLMClient()
  response = client.messages.create(
      model="claude-opus-4-7",
      system="...",
      messages=[{"role": "user", "content": "..."}],
  )
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator

try:
    from anthropic import Anthropic, APIError, RateLimitError, APIConnectionError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic SDK not installed. Run: pip install anthropic --break-system-packages", file=sys.stderr)


# 加载 .env
def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip() and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


load_env()


class LLMClient:
    """LLM 客户端封装"""

    # 定价（美元/1M tokens，2024 年）
    PRICING = {
        "claude-opus-4-7": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
        "claude-haiku-4-5": {"input": 0.25, "output": 1.25},
    }

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Set environment variable or pass api_key."
            )

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic SDK not installed")

        self.client = Anthropic(api_key=self.api_key)
        self.max_retries = max_retries
        self.total_cost = 0.0  # 累计成本（美元）

    def messages_create(
        self,
        model: str,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        thinking: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        同步调用 LLM
        
        Args:
            model: 模型名
            system: 系统提示
            messages: 消息列表
            max_tokens: 最大输出 tokens
            temperature: 温度
            thinking: 思考配置 {"enabled": True, "budget_tokens": 8000}
            tools: 工具列表
        """
        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": messages,
        }

        if thinking and thinking.get("enabled"):
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking.get("budget_tokens", 8000),
            }

        if tools:
            params["tools"] = tools

        params.update(kwargs)

        # 重试逻辑
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(**params)

                # 计算成本
                if response.usage:
                    cost = self._calculate_cost(
                        model, response.usage.input_tokens, response.usage.output_tokens
                    )
                    self.total_cost += cost

                return {
                    "id": response.id,
                    "model": response.model,
                    "content": self._extract_content(response),
                    "stop_reason": response.stop_reason,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                    },
                    "raw": response,
                }

            except RateLimitError as e:
                last_error = e
                wait = 2 ** attempt
                print(f"  Rate limit hit, waiting {wait}s ...", file=sys.stderr)
                time.sleep(wait)

            except APIConnectionError as e:
                last_error = e
                wait = 2 ** attempt
                print(f"  Connection error, retrying in {wait}s ...", file=sys.stderr)
                time.sleep(wait)

            except APIError as e:
                last_error = e
                if e.status_code and e.status_code < 500:
                    raise  # 4xx 不重试
                wait = 2 ** attempt
                print(f"  API error {e.status_code}, retrying ...", file=sys.stderr)
                time.sleep(wait)

        raise RuntimeError(f"LLM call failed after {self.max_retries} attempts: {last_error}")

    def messages_stream(
        self,
        model: str,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs,
    ) -> Iterator[str]:
        """流式调用"""
        with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages,
            **kwargs,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _extract_content(self, response) -> str:
        """提取响应文本"""
        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "".join(parts)

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """计算调用成本（美元）"""
        pricing = self.PRICING.get(model, self.PRICING["claude-opus-4-7"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost


# 便捷函数
_default_client = None

def get_client() -> LLMClient:
    """获取默认 LLM 客户端"""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


if __name__ == "__main__":
    # 测试
    if not ANTHROPIC_AVAILABLE:
        print("anthropic SDK not available, skipping test")
        sys.exit(0)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set, skipping test")
        sys.exit(0)

    client = LLMClient()
    response = client.messages_create(
        model="claude-haiku-4-5",
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Say 'Hello' in 3 languages."}],
        max_tokens=100,
    )
    print("Response:", response["content"])
    print("Usage:", response["usage"])
    print(f"Cost: ${client.total_cost:.6f}")
