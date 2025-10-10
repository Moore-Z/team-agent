#!/usr/bin/env python3
"""
Confluence 权限调试工具

专门用于诊断调试模式下的权限问题
"""

import os
import sys
from dotenv import load_dotenv
import requests

# 确保能找到项目模块
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def debug_confluence_connection():
    """详细调试 Confluence 连接"""
    print("🔍 Confluence 连接调试报告")
    print("=" * 60)

    # 1. 环境信息
    print(f"\n📊 运行环境:")
    print(f"   🐍 Python: {sys.executable}")
    print(f"   📁 工作目录: {os.getcwd()}")
    print(f"   📄 脚本位置: {__file__}")

    # 2. 检查 .env 文件
    print(f"\n📄 .env 文件检查:")
    env_paths = [
        '.env',
        os.path.join(project_root, '.env'),
        '/home/zhumoore/projects/team-agent/.env'
    ]

    env_file_found = None
    for env_path in env_paths:
        if os.path.exists(env_path):
            env_file_found = os.path.abspath(env_path)
            print(f"   ✅ 找到: {env_file_found}")
            break

    if not env_file_found:
        print(f"   ❌ 未找到 .env 文件")
        return

    # 3. 加载环境变量
    load_dotenv(env_file_found)
    print(f"\n🔧 环境变量加载:")

    confluence_url = os.getenv('CONFLUENCE_URL')
    username = os.getenv('CONFLUENCE_USERNAME')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')
    space_key = os.getenv('CONFLUENCE_PERSONAL_SPACE_KEY')

    # 检查变量是否存在
    vars_check = {
        'CONFLUENCE_URL': confluence_url,
        'CONFLUENCE_USERNAME': username,
        'CONFLUENCE_API_TOKEN': api_token,
        'CONFLUENCE_PERSONAL_SPACE_KEY': space_key
    }

    for var_name, var_value in vars_check.items():
        if var_value:
            if 'TOKEN' in var_name:
                display = f"{var_value[:4]}***{var_value[-4:]}"
            else:
                display = var_value
            print(f"   ✅ {var_name}: {display}")
        else:
            print(f"   ❌ {var_name}: 未设置")
            return

    # 4. 测试基本连接
    print(f"\n🌐 网络连接测试:")

    try:
        # 构造基本认证
        import base64
        credentials = base64.b64encode(f"{username}:{api_token}".encode()).decode()
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }

        # 测试基本连接 - 修正API路径
        test_url = f"{confluence_url}/wiki/rest/api/space"
        print(f"   🔍 测试URL: {test_url}")

        response = requests.get(test_url, headers=headers, timeout=10)

        print(f"   📊 响应状态: {response.status_code}")
        print(f"   📊 响应头: {dict(response.headers)}")

        if response.status_code == 200:
            print(f"   ✅ 连接成功!")
            data = response.json()
            print(f"   📊 找到 {len(data.get('results', []))} 个空间")
        elif response.status_code == 401:
            print(f"   ❌ 认证失败 (401)")
            print(f"   💡 可能原因: API Token无效或用户名错误")
        elif response.status_code == 403:
            print(f"   ❌ 权限被拒绝 (403)")
            print(f"   💡 可能原因: 用户没有访问权限")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            print(f"   📄 响应内容: {response.text[:200]}...")

    except Exception as e:
        print(f"   ❌ 连接异常: {e}")

    # 5. 测试使用 atlassian 库
    print(f"\n📚 Atlassian 库测试:")

    try:
        from atlassian import Confluence

        confluence = Confluence(
            url=confluence_url,
            username=username,
            password=api_token
        )

        # 测试获取空间
        spaces = confluence.get_all_spaces()
        print(f"   ✅ 通过 atlassian 库成功连接")
        print(f"   📊 找到 {len(spaces.get('results', []))} 个空间")

    except Exception as e:
        print(f"   ❌ atlassian 库连接失败: {e}")

    # 6. 检查可能的代理/网络设置
    print(f"\n🌍 网络环境检查:")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False

    for proxy_var in proxy_vars:
        proxy_value = os.getenv(proxy_var)
        if proxy_value:
            print(f"   🔍 {proxy_var}: {proxy_value}")
            proxy_found = True

    if not proxy_found:
        print(f"   ✅ 未检测到代理设置")

    # 7. 调试模式特定检查
    print(f"\n🐛 调试模式检查:")
    debug_indicators = {
        'PYTHONDEBUG': os.getenv('PYTHONDEBUG'),
        'PYCHARM_HOSTED': os.getenv('PYCHARM_HOSTED'),
        'VSCODE_PID': os.getenv('VSCODE_PID'),
        'PYTEST_CURRENT_TEST': os.getenv('PYTEST_CURRENT_TEST'),
        '_': os.getenv('_')  # 通常包含启动命令
    }

    for var, value in debug_indicators.items():
        if value:
            print(f"   🔍 {var}: {value}")

if __name__ == "__main__":
    debug_confluence_connection()