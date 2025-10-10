#!/usr/bin/env python3
"""
Test accessing specific Confluence space
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.connectors.confluence import ConfluenceConnector
import json

load_dotenv()

# Load environment variables
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
USERNAME = os.getenv('CONFLUENCE_USERNAME')
API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')
PERSONAL_SPACE_KEY = os.getenv('CCONFLUENCE_PERSONAL_SPACE_KEY')

def main():
    try:
        # Initialize connector
        print("Connecting to Confluence...")
        connector = ConfluenceConnector(CONFLUENCE_URL, USERNAME, API_TOKEN)

        # Your personal space key from the URL
        PERSONAL_SPACE_KEY = "~7012195a0ae39f62540e28c6200609b5f4fcf"

        print(f"Accessing personal space: {PERSONAL_SPACE_KEY}")

        # Try to get space info
        try:
            space_info = connector.fetch_space_by_key(PERSONAL_SPACE_KEY)
            print(f"Space name: {space_info.get('name', 'Unknown')}")
            print(f"Space type: {space_info.get('type', 'Unknown')}")
        except Exception as e:
            print(f"Could not fetch space info: {e}")

        # Fetch pages from your personal space
        print("Fetching pages from personal space...")
        pages = connector.fetch_pages(PERSONAL_SPACE_KEY, limit=10)
        print(f"Found {len(pages)} pages")

        if pages:
            for i, page in enumerate(pages):
                print(f"{i+1}. {page['title']} (ID: {page['id']})")
                print(type(page))

            # Process the first page
            first_page = pages[0]
            print(f"\nProcessing page: {first_page['title']}")

            processed = connector.process_page_content(first_page)

            # Print results
            print("\n" + "="*50)
            print(f"Page ID: {processed['id']}")
            print(f"Title: {processed['metadata']['title']}")
            print(f"URL: {processed['metadata']['url']}")
            print(f"Content preview: {processed['content'][:300]}...")
            print("="*50)

            # Save to file
            with open('personal_space_data.json', 'w', encoding='utf-8') as f:
                json.dump(processed, f, indent=2, ensure_ascii=False)
            print("Data saved to personal_space_data.json")
        else:
            print("No pages found in personal space")

            # Try alternative approach - get all spaces and find yours
            print("\nTrying to find your space in all available spaces...")
            all_spaces = connector.fetch_spaces()
            print(f"Found {len(all_spaces)} total spaces")

            for space in all_spaces:
                if PERSONAL_SPACE_KEY in space.get('key', ''):
                    print(f"Found matching space: {space['name']} ({space['key']})")
                    break
            else:
                print("Personal space not found in available spaces")
                print("Available spaces:")
                for space in all_spaces[:5]:
                    print(f"  - {space['key']}: {space['name']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()