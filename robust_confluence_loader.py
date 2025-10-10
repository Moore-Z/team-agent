#!/usr/bin/env python3
"""
Robust Confluence 加载器

确保在任何环境下都能正确加载配置和连接 Confluence
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def setup_robust_environment():
    """
    设置健壮的运行环境
    无论在哪种模式下运行都能正确工作
    """
    # 1. 确定项目根目录
    current_file = Path(__file__).resolve()
    project_root = current_file.parent

    # 向上查找，直到找到包含 backend 目录的文件夹
    while project_root != project_root.parent:
        if (project_root / 'backend').exists():
            break
        project_root = project_root.parent

    print(f"🔍 项目根目录: {project_root}")

    # 2. 添加到 Python 路径
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 3. 强制加载 .env 文件
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)  # override=True 强制重新加载
        print(f"✅ 加载 .env 文件: {env_file}")
    else:
        print(f"❌ 未找到 .env 文件: {env_file}")

    # 4. 设置工作目录（如果需要）
    os.chdir(project_root)
    print(f"✅ 设置工作目录: {project_root}")

    return project_root

def create_robust_confluence_connector():
    """
    创建健壮的 Confluence 连接器
    """
    # 确保环境正确设置
    setup_robust_environment()

    # 导入模块
    from backend.connectors.confluenceToJason import FormConfluenceDataToPersist

    # 显式读取环境变量
    confluence_url = os.getenv('CONFLUENCE_URL')
    username = os.getenv('CONFLUENCE_USERNAME')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')

    print(f"\n🔧 配置检查:")
    print(f"   URL: {'✅' if confluence_url else '❌'}")
    print(f"   用户名: {'✅' if username else '❌'}")
    print(f"   API Token: {'✅' if api_token else '❌'}")

    if not all([confluence_url, username, api_token]):
        raise ValueError("缺少必要的 Confluence 配置")

    # 创建连接器
    connector = FormConfluenceDataToPersist(
        url=confluence_url,
        username=username,
        api_token=api_token
    )

    print(f"✅ Confluence 连接器创建成功")
    return connector

def main():
    """主函数 - 演示健壮的连接"""
    try:
        print("🚀 健壮的 Confluence 连接测试")
        print("=" * 50)

        # 创建连接器
        connector = create_robust_confluence_connector()

        # 测试连接
        print(f"\n📂 测试获取空间...")
        spaces = connector.fetch_spaces()
        print(f"✅ 成功获取 {len(spaces)} 个空间")

        for space in spaces[:2]:
            print(f"   - {space.get('name')} ({space.get('key')})")

        print(f"\n🎉 测试完成!")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()