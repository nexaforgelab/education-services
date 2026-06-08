#!/usr/bin/env python3
"""
run_agent_real.py — 真实运行 Agent

基于 LLM Client 调用真实 Agent 流程（严格无 mock 模式），支持：
  - 加载 system prompt（来自 .md 文件）
  - 加载 skills（来自 SKILL.md）
  - 解析命令
  - 调用真实 LLM（必须 ANTHROPIC_API_KEY）
  - 写入最终输出

用法:
  python scripts/run_agent_real.py \
    --agent textbook-teaching-agent \
    --system-file plugins/agent-plugins/textbook-teaching-agent/agents/textbook-teaching-agent.md \
    --command "/lesson-plan" \
    --args "[\"有理数加减法\", \"45\", \"中等\"]" \
    --output-dir ./out/
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# 加入 scripts 目录
sys.path.insert(0, str(Path(__file__).parent))

try:
    import yaml
except ImportError:
    print("Error: pip install pyyaml --break-system-packages", file=sys.stderr)
    sys.exit(1)

from llm_client import LLMClient, get_client


REPO_ROOT = Path(__file__).parent.parent


def load_markdown_frontmatter(path: Path) -> Dict[str, Any]:
    """加载 Markdown frontmatter"""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return {}


def load_system_prompt(path: Path) -> str:
    """加载 system prompt（去掉 frontmatter）"""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    return parts[2].strip()


def load_skills(plugin_dirs: List[Path]) -> str:
    """加载所有 SKILL.md 内容"""
    skills_content = []
    for plugin_dir in plugin_dirs:
        for skill_md in plugin_dir.rglob("SKILL.md"):
            frontmatter = load_markdown_frontmatter(skill_md)
            name = frontmatter.get("name", skill_md.parent.name)
            description = frontmatter.get("description", "")
            content = load_system_prompt(skill_md)
            skills_content.append(
                f"\n\n## Skill: {name}\n{description}\n\n{content}"
            )
    return "\n".join(skills_content)


def parse_command(command_str: str) -> Dict[str, str]:
    """解析 /command"""
    if not command_str.startswith("/"):
        command_str = "/" + command_str
    return {"name": command_str.lstrip("/")}


def run_real_agent(
    agent_name: str,
    system_prompt_path: Path,
    plugin_dirs: List[Path],
    command: str,
    args: List[str],
    output_dir: Path,
    user_role: str = "teacher",
    model: str = "claude-opus-4-7",
    max_tokens: int = 8000,
) -> Dict[str, Any]:
    """运行真实 Agent"""

    print(f"🤖 运行 Agent: {agent_name}")
    print(f"   Model: {model}")
    print(f"   命令: {command} {' '.join(args)}")

    # 1. 加载 system prompt
    system = load_system_prompt(system_prompt_path)

    # 2. 加载 skills
    skills_text = load_skills(plugin_dirs)
    full_system = f"{system}\n\n# 可用 Skills\n{skills_text}"

    # 3. 构造 user message
    user_message = f"""
{command} {' '.join(args)}

请根据 system prompt 和 skills 完成这个任务。
输出必须是结构化的 Markdown / JSON，便于后续处理。
所有教材相关结论必须引用页码（[教材原文 p.X]）。
"""

    # 4. 调用 LLM
    print("   调用 LLM ...")
    t0 = time.time()
    client = get_client()

    try:
        response = client.messages_create(
            model=model,
            system=full_system,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=max_tokens,
            temperature=0.3,
            thinking={"enabled": True, "budget_tokens": 8000},
        )
        elapsed = time.time() - t0
        print(f"   ✓ 完成 ({elapsed:.1f}s)")
        print(f"   Tokens: in={response['usage']['input_tokens']}, out={response['usage']['output_tokens']}")
        print(f"   累计成本: ${client.total_cost:.4f}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        raise

    # 5. 写输出
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    out_subdir = output_dir / f"{command.lstrip('/')}_{timestamp}"
    out_subdir.mkdir(parents=True, exist_ok=True)

    # 主输出
    main_file = out_subdir / "output.md"
    main_file.write_text(response["content"], encoding="utf-8")

    # 元数据
    meta_file = out_subdir / "meta.json"
    meta = {
        "agent": agent_name,
        "command": command,
        "args": args,
        "user_role": user_role,
        "model": model,
        "created_at": timestamp,
        "elapsed_seconds": elapsed,
        "usage": response["usage"],
        "total_cost_usd": client.total_cost,
    }
    meta_file.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n✅ 输出:")
    print(f"   {main_file}")
    print(f"   {meta_file}")

    return {
        "output_dir": str(out_subdir),
        "output_file": str(main_file),
        "usage": response["usage"],
        "cost": client.total_cost,
    }


def main():
    parser = argparse.ArgumentParser(description="运行真实 Agent")
    parser.add_argument("--agent", required=True, help="Agent 名")
    parser.add_argument("--system-file", required=True, help="system prompt 文件")
    parser.add_argument(
        "--plugin-dirs",
        nargs="+",
        default=["plugins/vertical-plugins/education-core",
                 "plugins/vertical-plugins/subject-math"],
        help="plugin 目录列表"
    )
    parser.add_argument("--command", required=True, help="命令，如 /lesson-plan")
    parser.add_argument("--args", default="[]", help="JSON 字符串参数列表")
    parser.add_argument("--output-dir", default="./out/")
    parser.add_argument("--user-role", default="teacher", help="teacher/parent")
    parser.add_argument("--model", default="claude-opus-4-7")
    parser.add_argument("--max-tokens", type=int, default=8000)
    args = parser.parse_args()

    try:
        cmd_args = json.loads(args.args)
    except json.JSONDecodeError:
        cmd_args = args.args.split() if args.args else []

    plugin_dirs = [Path(p) for p in args.plugin_dirs]

    run_real_agent(
        agent_name=args.agent,
        system_prompt_path=Path(args.system_file),
        plugin_dirs=plugin_dirs,
        command=args.command,
        args=cmd_args,
        output_dir=Path(args.output_dir),
        user_role=args.user_role,
        model=args.model,
        max_tokens=args.max_tokens,
    )


if __name__ == "__main__":
    main()
