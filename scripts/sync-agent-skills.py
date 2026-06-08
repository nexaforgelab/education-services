#!/usr/bin/env python3
"""
sync-agent-skills.py — 同步 vertical plugin 的 skills 到使用它的 agent

参考 financial-services 的 sync 模式：维护一份 "skill 来源 → 使用 agent" 的映射，
确保新增 skill 自动同步到所有相关 agent。

用法:
  python scripts/sync-agent-skills.py --check   # 检查是否有未同步的
  python scripts/sync-agent-skills.py --sync    # 实际同步
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set


REPO_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"


def load_plugin_json(path: Path) -> dict:
    """加载 .claude-plugin/plugin.json"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def discover_vertical_plugins() -> Dict[str, dict]:
    """发现所有 vertical plugin"""
    result = {}
    vdir = PLUGINS_DIR / "vertical-plugins"
    if not vdir.exists():
        return result
    for plugin_dir in vdir.iterdir():
        if not plugin_dir.is_dir():
            continue
        pj = plugin_dir / ".claude-plugin" / "plugin.json"
        if pj.exists():
            result[plugin_dir.name] = load_plugin_json(pj)
    return result


def discover_agent_plugins() -> Dict[str, dict]:
    """发现所有 agent plugin"""
    result = {}
    adir = PLUGINS_DIR / "agent-plugins"
    if not adir.exists():
        return result
    for plugin_dir in adir.iterdir():
        if not plugin_dir.is_dir():
            continue
        pj = plugin_dir / ".claude-plugin" / "plugin.json"
        if pj.exists():
            result[plugin_dir.name] = load_plugin_json(pj)
    return result


def get_skills_in_plugin(plugin: dict, base_path: Path) -> List[Path]:
    """获取 plugin 声明的所有 skills（解析为绝对路径）"""
    skills = []
    for skill_rel in plugin.get("skills", []):
        # 处理 "./skills/x/SKILL.md" 形式
        skill_rel = skill_rel.lstrip("./")
        skill_path = base_path / skill_rel
        skills.append(skill_path)
    return skills


def check_sync() -> List[str]:
    """检查是否有未同步的 skill"""
    issues = []

    verticals = discover_vertical_plugins()
    agents = discover_agent_plugins()

    for vname, vplugin in verticals.items():
        vbase = PLUGINS_DIR / "vertical-plugins" / vname
        vskills = get_skills_in_plugin(vplugin, vbase)

        for aname, aplugin in agents.items():
            # 检查 agent 是否依赖该 vertical
            deps = aplugin.get("depends_on", [])
            depends = any(vname in d for d in deps)
            if not depends:
                continue

            # 检查 agent 的 plugin.json 是否列了这些 skills
            askills = set(get_skills_in_plugin(apluin, PLUGINS_DIR / "agent-plugins" / aname))
            vskills_set = set(vskills)
            missing = vskills_set - askills

            if missing:
                issues.append(
                    f"Agent '{aname}' 依赖 '{vname}' 但缺少 skills:\n"
                    + "\n".join(f"  - {m.relative_to(REPO_ROOT)}" for m in missing)
                )
    return issues


def sync() -> int:
    """实际同步：把 vertical 的 skills 加到 agent 的 plugin.json"""
    agents = discover_agent_plugins()
    changes = 0

    for aname, aplugin in agents.items():
        abase = PLUGINS_DIR / "agent-plugins" / aname
        apj = abase / ".claude-plugin" / "plugin.json"
        deps = aplugin.get("depends_on", [])

        for dep in deps:
            # 提取 vertical plugin 名
            vname = Path(dep).name
            vbase = PLUGINS_DIR / "vertical-plugins" / vname
            vplugin_pj = vbase / ".claude-plugin" / "plugin.json"
            if not vplugin_pj.exists():
                continue
            vplugin = load_plugin_json(vplugin_pj)
            vskills = get_skills_in_plugin(vplugin, vbase)

            current_skills = aplugin.get("skills", [])
            for s in vskills:
                rel = s.relative_to(REPO_ROOT)
                if str(rel) not in current_skills:
                    aplugin.setdefault("skills", []).append(str(rel))
                    changes += 1

        if changes:
            with open(apj, "w", encoding="utf-8") as f:
                json.dump(apluin, f, ensure_ascii=False, indent=2)

    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="只检查，不修改")
    parser.add_argument("--sync", action="store_true", help="实际同步")
    args = parser.parse_args()

    if args.check:
        issues = check_sync()
        if issues:
            print("❌ 发现未同步的 skill：")
            for i in issues:
                print(f"  {i}\n")
            sys.exit(1)
        else:
            print("✅ 所有 skill 已同步")
    elif args.sync:
        changes = sync()
        print(f"✅ 同步完成，更新了 {changes} 项")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
