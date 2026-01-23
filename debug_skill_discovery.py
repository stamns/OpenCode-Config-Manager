#!/usr/bin/env python3
"""
调试 Skill 发现问题
"""

import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from opencode_config_manager_fluent import SkillDiscovery


def debug_skill_discovery():
    """调试 Skill 发现"""
    print("=" * 80)
    print("Skill 发现调试")
    print("=" * 80)
    print()

    # 1. 检查当前工作目录
    print(f"当前工作目录: {Path.cwd()}")
    print()

    # 2. 检查所有搜索路径
    print("搜索路径:")
    print("-" * 80)

    all_paths = {**SkillDiscovery.SKILL_PATHS, **SkillDiscovery.get_project_paths()}

    for source, path in all_paths.items():
        exists = "✓" if path.exists() else "✗"
        print(f"{exists} {source:20} {path}")

        if path.exists():
            try:
                skills_in_path = list(path.iterdir())
                print(f"   包含 {len(skills_in_path)} 个子目录/文件:")
                for item in skills_in_path[:5]:  # 只显示前5个
                    item_type = "DIR" if item.is_dir() else "FILE"
                    print(f"     - [{item_type}] {item.name}")
                if len(skills_in_path) > 5:
                    print(f"     ... 还有 {len(skills_in_path) - 5} 个")
            except Exception as e:
                print(f"   错误: {str(e)}")
        print()

    # 3. 发现所有 skills
    print("发现的 Skills:")
    print("-" * 80)

    skills = SkillDiscovery.discover_all()

    if not skills:
        print("未发现任何 Skills")
    else:
        for skill in skills:
            print(f"✓ {skill.name}")
            print(f"  来源: {skill.source}")
            print(f"  路径: {skill.path}")
            print(f"  描述: {skill.description[:60]}...")
            print()

    print("=" * 80)
    print(f"总计: {len(skills)} 个 Skills")
    print("=" * 80)


if __name__ == "__main__":
    debug_skill_discovery()
