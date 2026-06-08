#!/usr/bin/env python3
"""
validate.py — 校验项目结构和配置是否符合 financial-services 风格的标准

检查项:
  1. 所有 .claude-plugin/plugin.json 是有效 JSON
  2. agent-plugins 与 managed-agent-cookbooks 命名一致
  3. 所有 SKILL.md 都有 frontmatter
  4. 所有 command 文件都有 frontmatter
  5. subagent 权限隔离（只有 feedback-writer 有 Write）
  6. MCP servers 配置正确
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple


REPO_ROOT = Path(__file__).parent.parent


def check_plugin_json() -> List[str]:
    """检查所有 plugin.json 是否有效"""
    issues = []
    for pj in REPO_ROOT.rglob(".claude-plugin/plugin.json"):
        try:
            with open(pj, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "name" not in data:
                issues.append(f"❌ {pj.relative_to(REPO_ROOT)}: missing 'name'")
        except json.JSONDecodeError as e:
            issues.append(f"❌ {pj.relative_to(REPO_ROOT)}: invalid JSON: {e}")
    return issues


def check_skill_frontmatter() -> List[str]:
    """检查所有 SKILL.md 是否有 frontmatter"""
    issues = []
    for sm in REPO_ROOT.rglob("SKILL.md"):
        with open(sm, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.startswith("---"):
            issues.append(f"❌ {sm.relative_to(REPO_ROOT)}: missing frontmatter")
            continue
        # 检查 frontmatter 包含 name 和 description
        if "name:" not in content[:500]:
            issues.append(f"❌ {sm.relative_to(REPO_ROOT)}: missing 'name:' in frontmatter")
        if "description:" not in content[:1000]:
            issues.append(f"❌ {sm.relative_to(REPO_ROOT)}: missing 'description:' in frontmatter")
    return issues


def check_command_frontmatter() -> List[str]:
    """检查所有 command 文件"""
    issues = []
    for cm in REPO_ROOT.rglob("commands/*.md"):
        with open(cm, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.startswith("---"):
            issues.append(f"❌ {cm.relative_to(REPO_ROOT)}: missing frontmatter")
    return issues


def check_agent_cookbook_alignment() -> List[str]:
    """检查 agent-plugins 和 managed-agent-cookbooks 命名一致"""
    issues = []
    agents_dir = REPO_ROOT / "plugins" / "agent-plugins"
    cookbooks_dir = REPO_ROOT / "managed-agent-cookbooks"

    if not agents_dir.exists() or not cookbooks_dir.exists():
        return issues

    agent_names = {d.name for d in agents_dir.iterdir() if d.is_dir()}
    cookbook_names = {d.name for d in cookbooks_dir.iterdir() if d.is_dir()}

    for a in agent_names:
        if a not in cookbook_names:
            issues.append(f"⚠️  Agent '{a}' 缺少对应 cookbook 在 managed-agent-cookbooks/")

    for c in cookbook_names:
        if c not in agent_names:
            issues.append(f"⚠️  Cookbook '{c}' 缺少对应 agent 在 agent-plugins/")
    return issues


def check_subagent_permissions() -> List[str]:
    """检查 subagent 权限隔离：只有 feedback-writer 有 Write"""
    issues = []
    cookbook_dir = REPO_ROOT / "managed-agent-cookbooks"
    if not cookbook_dir.exists():
        return issues

    for sub in cookbook_dir.rglob("subagents/*.yaml"):
        with open(sub, "r", encoding="utf-8") as f:
            content = f.read()
        is_writer = "feedback-writer" in sub.name
        has_write = "Write, enabled: true" in content or "Write: enabled" in content

        if is_writer and not has_write:
            issues.append(f"❌ {sub.relative_to(REPO_ROOT)}: feedback-writer 必须有 Write 权限")
        elif not is_writer and has_write:
            issues.append(f"❌ {sub.relative_to(REPO_ROOT)}: 非 feedback-writer 不应有 Write 权限")
    return issues


def check_mcp_config() -> List[str]:
    """检查 MCP 配置"""
    issues = []
    for mcp in REPO_ROOT.rglob(".mcp.json"):
        try:
            with open(mcp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "mcpServers" not in data:
                issues.append(f"❌ {mcp.relative_to(REPO_ROOT)}: missing 'mcpServers' key")
        except json.JSONDecodeError as e:
            issues.append(f"❌ {mcp.relative_to(REPO_ROOT)}: invalid JSON: {e}")
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="严格模式：警告也作为错误")
    args = parser.parse_args()

    print("🔍 Validating education-services structure...\n")

    all_issues = []
    for name, check in [
        ("plugin.json 校验", check_plugin_json),
        ("SKILL.md frontmatter", check_skill_frontmatter),
        ("command frontmatter", check_command_frontmatter),
        ("agent-cookbook 对齐", check_agent_cookbook_alignment),
        ("subagent 权限隔离", check_subagent_permissions),
        ("MCP 配置", check_mcp_config),
    ]:
        issues = check()
        if issues:
            print(f"❌ {name}:")
            for i in issues:
                print(f"   {i}")
            all_issues.extend(issues)
        else:
            print(f"✅ {name}")

    print()
    if all_issues:
        print(f"❌ 发现 {len(all_issues)} 个问题")
        if args.strict:
            sys.exit(1)
    else:
        print("✅ 所有检查通过")


if __name__ == "__main__":
    main()
