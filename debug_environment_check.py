#!/usr/bin/env python3
"""
Debug environment check tool
Used to analyze differences between debug mode and direct execution
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check current runtime environment"""
    print("🔍 Environment Check Report")
    print("=" * 50)

    # 1. Working directory
    print(f"📁 Current working directory: {os.getcwd()}")

    # 2. Python path
    print(f"\n🐍 Python executable: {sys.executable}")
    print(f"🐍 Python version: {sys.version}")

    # 3. Script location
    print(f"\n📄 Current script location: {__file__}")
    print(f"📄 Script absolute path: {os.path.abspath(__file__)}")

    # 4. First few sys.path entries
    print(f"\n🛤️ Python module search paths:")
    for i, path in enumerate(sys.path[:5], 1):
        print(f"   {i}. {path}")

    # 5. Environment variable check
    print(f"\n🔧 Environment variable check:")

    # Check .env file locations
    possible_env_files = [
        '.env',
        '../.env',
        '../../.env',
        '/home/zhumoore/projects/team-agent/.env'
    ]

    for env_file in possible_env_files:
        if os.path.exists(env_file):
            print(f"   ✅ Found .env file: {os.path.abspath(env_file)}")
            break
    else:
        print(f"   ❌ .env file not found")

    # Load environment variables
    load_dotenv()

    # Check key environment variables
    env_vars = {
        'CONFLUENCE_URL': os.getenv('CONFLUENCE_URL'),
        'CONFLUENCE_USERNAME': os.getenv('CONFLUENCE_USERNAME'),
        'CONFLUENCE_API_TOKEN': os.getenv('CONFLUENCE_API_TOKEN'),
        'CONFLUENCE_PERSONAL_SPACE_KEY': os.getenv('CONFLUENCE_PERSONAL_SPACE_KEY')
    }

    for var_name, var_value in env_vars.items():
        if var_value:
            # Hide sensitive information
            if 'TOKEN' in var_name or 'PASSWORD' in var_name:
                display_value = f"{var_value[:4]}***{var_value[-4:]}" if len(var_value) > 8 else "***"
            else:
                display_value = var_value
            print(f"   ✅ {var_name}: {display_value}")
        else:
            print(f"   ❌ {var_name}: Not set")

    # 6. Check debug-related environment variables
    print(f"\n🐛 Debug-related environment variables:")
    debug_vars = ['PYTHONDEBUG', 'PYTHONPATH', 'DEBUG', 'PYCHARM_HOSTED']
    for var in debug_vars:
        value = os.getenv(var)
        if value:
            print(f"   🔍 {var}: {value}")

    # 7. Check IDE-related
    if 'PYCHARM_HOSTED' in os.environ:
        print(f"\n🔧 Detected PyCharm debug environment")
    elif 'VSCODE_PID' in os.environ:
        print(f"\n🔧 Detected VS Code environment")
    else:
        print(f"\n🔧 No specific IDE environment detected")

if __name__ == "__main__":
    check_environment()