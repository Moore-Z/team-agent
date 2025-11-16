#!/usr/bin/env python3
"""
Confluence Permission Debug Tool

Specifically designed for diagnosing permission issues in debug mode
"""

import os
import sys
from dotenv import load_dotenv
import requests

# Ensure project modules can be found
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def debug_confluence_connection():
    """Detailed debugging of Confluence connection"""
    print("🔍 Confluence Connection Debug Report")
    print("=" * 60)

    # 1. Environment information
    print(f"\n📊 Runtime environment:")
    print(f"   🐍 Python: {sys.executable}")
    print(f"   📁 Working directory: {os.getcwd()}")
    print(f"   📄 Script location: {__file__}")

    # 2. Check .env file
    print(f"\n📄 .env file check:")
    env_paths = [
        '.env',
        os.path.join(project_root, '.env'),
        '/home/zhumoore/projects/team-agent/.env'
    ]

    env_file_found = None
    for env_path in env_paths:
        if os.path.exists(env_path):
            env_file_found = os.path.abspath(env_path)
            print(f"   ✅ Found: {env_file_found}")
            break

    if not env_file_found:
        print(f"   ❌ .env file not found")
        return

    # 3. Load environment variables
    load_dotenv(env_file_found)
    print(f"\n🔧 Environment variable loading:")

    confluence_url = os.getenv('CONFLUENCE_URL')
    username = os.getenv('CONFLUENCE_USERNAME')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')
    space_key = os.getenv('CONFLUENCE_PERSONAL_SPACE_KEY')

    # Check if variables exist
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
            print(f"   ❌ {var_name}: Not set")
            return

    # 4. Test basic connection
    print(f"\n🌐 Network connection test:")

    try:
        # Construct basic authentication
        import base64
        credentials = base64.b64encode(f"{username}:{api_token}".encode()).decode()
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }

        # Test basic connection - corrected API path
        test_url = f"{confluence_url}/wiki/rest/api/space"
        print(f"   🔍 Test URL: {test_url}")

        response = requests.get(test_url, headers=headers, timeout=10)

        print(f"   📊 Response status: {response.status_code}")
        print(f"   📊 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print(f"   ✅ Connection successful!")
            data = response.json()
            print(f"   📊 Found {len(data.get('results', []))} spaces")
        elif response.status_code == 401:
            print(f"   ❌ Authentication failed (401)")
            print(f"   💡 Possible cause: Invalid API token or incorrect username")
        elif response.status_code == 403:
            print(f"   ❌ Permission denied (403)")
            print(f"   💡 Possible cause: User does not have access permissions")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   📄 Response content: {response.text[:200]}...")

    except Exception as e:
        print(f"   ❌ Connection exception: {e}")

    # 5. Test using atlassian library
    print(f"\n📚 Atlassian library test:")

    try:
        from atlassian import Confluence

        confluence = Confluence(
            url=confluence_url,
            username=username,
            password=api_token
        )

        # Test getting spaces
        spaces = confluence.get_all_spaces()
        print(f"   ✅ Successfully connected via atlassian library")
        print(f"   📊 Found {len(spaces.get('results', []))} spaces")

    except Exception as e:
        print(f"   ❌ Atlassian library connection failed: {e}")

    # 6. Check possible proxy/network settings
    print(f"\n🌍 Network environment check:")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False

    for proxy_var in proxy_vars:
        proxy_value = os.getenv(proxy_var)
        if proxy_value:
            print(f"   🔍 {proxy_var}: {proxy_value}")
            proxy_found = True

    if not proxy_found:
        print(f"   ✅ No proxy settings detected")

    # 7. Debug mode specific checks
    print(f"\n🐛 Debug mode check:")
    debug_indicators = {
        'PYTHONDEBUG': os.getenv('PYTHONDEBUG'),
        'PYCHARM_HOSTED': os.getenv('PYCHARM_HOSTED'),
        'VSCODE_PID': os.getenv('VSCODE_PID'),
        'PYTEST_CURRENT_TEST': os.getenv('PYTEST_CURRENT_TEST'),
        '_': os.getenv('_')  # Usually contains startup command
    }

    for var, value in debug_indicators.items():
        if value:
            print(f"   🔍 {var}: {value}")

if __name__ == "__main__":
    debug_confluence_connection()