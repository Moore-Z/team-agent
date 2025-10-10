#!/usr/bin/env python3
"""
Basic Confluence connection test
"""

import os
from dotenv import load_dotenv
from atlassian import Confluence

load_dotenv()

# Load environment variables
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
USERNAME = os.getenv('CONFLUENCE_USERNAME')
API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')

def main():
    print(f"URL: {CONFLUENCE_URL}")
    print(f"Username: {USERNAME}")
    print(f"Token: {'***' + API_TOKEN[-4:] if API_TOKEN else 'None'}")
    print()

    try:
        # Direct connection test
        confluence = Confluence(
            url=CONFLUENCE_URL,
            username=USERNAME,
            password=API_TOKEN
        )

        print("Testing connection...")

        # Try the simplest possible call - test with spaces
        print("Available methods:", [method for method in dir(confluence) if not method.startswith('_')])

        # Try getting spaces instead
        spaces = confluence.get_all_spaces(limit=1)
        print(f"✅ Connected! Found {len(spaces.get('results', []))} spaces")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your CONFLUENCE_URL format (should be https://domain.atlassian.net)")
        print("2. Verify USERNAME is your email address")
        print("3. Make sure API_TOKEN is valid and has read permissions")
        print("4. Try accessing Confluence web interface first")

if __name__ == "__main__":
    main()