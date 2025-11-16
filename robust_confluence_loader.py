#!/usr/bin/env python3
"""
Robust Confluence Loader

Ensures proper configuration loading and Confluence connection in any environment
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def setup_robust_environment():
    """
    Set up robust runtime environment
    Works correctly regardless of which mode it runs in
    """
    # 1. Determine project root directory
    current_file = Path(__file__).resolve()
    project_root = current_file.parent

    # Search upward until finding folder containing backend directory
    while project_root != project_root.parent:
        if (project_root / 'backend').exists():
            break
        project_root = project_root.parent

    print(f"🔍 Project root directory: {project_root}")

    # 2. Add to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 3. Force load .env file
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)  # override=True forces reload
        print(f"✅ Loaded .env file: {env_file}")
    else:
        print(f"❌ .env file not found: {env_file}")

    # 4. Set working directory (if needed)
    os.chdir(project_root)
    print(f"✅ Set working directory: {project_root}")

    return project_root

def create_robust_confluence_connector():
    """
    Create robust Confluence connector
    """
    # Ensure environment is correctly set
    setup_robust_environment()

    # Import modules
    from backend.connectors.confluenceToJason import FormConfluenceDataToPersist

    # Explicitly read environment variables
    confluence_url = os.getenv('CONFLUENCE_URL')
    username = os.getenv('CONFLUENCE_USERNAME')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')

    print(f"\n🔧 Configuration check:")
    print(f"   URL: {'✅' if confluence_url else '❌'}")
    print(f"   Username: {'✅' if username else '❌'}")
    print(f"   API Token: {'✅' if api_token else '❌'}")

    if not all([confluence_url, username, api_token]):
        raise ValueError("Missing required Confluence configuration")

    # Create connector
    connector = FormConfluenceDataToPersist(
        url=confluence_url,
        username=username,
        api_token=api_token
    )

    print(f"✅ Confluence connector created successfully")
    return connector

def main():
    """Main function - demonstrate robust connection"""
    try:
        print("🚀 Robust Confluence connection test")
        print("=" * 50)

        # Create connector
        connector = create_robust_confluence_connector()

        # Test connection
        print(f"\n📂 Testing space retrieval...")
        spaces = connector.fetch_spaces()
        print(f"✅ Successfully retrieved {len(spaces)} spaces")

        for space in spaces[:2]:
            print(f"   - {space.get('name')} ({space.get('key')})")

        print(f"\n🎉 Test completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()