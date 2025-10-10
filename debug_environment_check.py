#!/usr/bin/env python3
"""
调试环境检查工具
用于分析调试模式和直接运行的差异
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """检查当前运行环境"""
    print("🔍 环境检查报告")
    print("=" * 50)

    # 1. 工作目录
    print(f"📁 当前工作目录: {os.getcwd()}")

    # 2. Python路径
    print(f"\n🐍 Python可执行文件: {sys.executable}")
    print(f"🐍 Python版本: {sys.version}")

    # 3. 脚本位置
    print(f"\n📄 当前脚本位置: {__file__}")
    print(f"📄 脚本绝对路径: {os.path.abspath(__file__)}")

    # 4. sys.path 前几个路径
    print(f"\n🛤️ Python模块搜索路径:")
    for i, path in enumerate(sys.path[:5], 1):
        print(f"   {i}. {path}")

    # 5. 环境变量检查
    print(f"\n🔧 环境变量检查:")

    # 检查 .env 文件位置
    possible_env_files = [
        '.env',
        '../.env',
        '../../.env',
        '/home/zhumoore/projects/team-agent/.env'
    ]

    for env_file in possible_env_files:
        if os.path.exists(env_file):
            print(f"   ✅ 找到 .env 文件: {os.path.abspath(env_file)}")
            break
    else:
        print(f"   ❌ 未找到 .env 文件")

    # 加载环境变量
    load_dotenv()

    # 检查关键环境变量
    env_vars = {
        'CONFLUENCE_URL': os.getenv('CONFLUENCE_URL'),
        'CONFLUENCE_USERNAME': os.getenv('CONFLUENCE_USERNAME'),
        'CONFLUENCE_API_TOKEN': os.getenv('CONFLUENCE_API_TOKEN'),
        'CONFLUENCE_PERSONAL_SPACE_KEY': os.getenv('CONFLUENCE_PERSONAL_SPACE_KEY')
    }

    for var_name, var_value in env_vars.items():
        if var_value:
            # 隐藏敏感信息
            if 'TOKEN' in var_name or 'PASSWORD' in var_name:
                display_value = f"{var_value[:4]}***{var_value[-4:]}" if len(var_value) > 8 else "***"
            else:
                display_value = var_value
            print(f"   ✅ {var_name}: {display_value}")
        else:
            print(f"   ❌ {var_name}: 未设置")

    # 6. 检查调试相关环境变量
    print(f"\n🐛 调试相关环境变量:")
    debug_vars = ['PYTHONDEBUG', 'PYTHONPATH', 'DEBUG', 'PYCHARM_HOSTED']
    for var in debug_vars:
        value = os.getenv(var)
        if value:
            print(f"   🔍 {var}: {value}")

    # 7. 检查IDE相关
    if 'PYCHARM_HOSTED' in os.environ:
        print(f"\n🔧 检测到 PyCharm 调试环境")
    elif 'VSCODE_PID' in os.environ:
        print(f"\n🔧 检测到 VS Code 环境")
    else:
        print(f"\n🔧 未检测到特定IDE环境")

if __name__ == "__main__":
    check_environment()