# connectors/confluence.py
from atlassian import Confluence
from typing import List, Dict
import re
from datetime import datetime

class ConfluenceConnector:
    def __init__(self, url: str, username: str, api_token: str):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=api_token
        )
        
    def fetch_spaces(self) -> List[Dict]:
        """Fetch all accessible spaces"""
        spaces = self.confluence.get_all_spaces()
        return spaces['results']
    
    def fetch_pages(self, space_key: str, limit: int = 100) -> List[Dict]:
        """Fetch all pages in a space"""
        pages = self.confluence.get_all_pages_from_space(
            space_key, 
            start=0, 
            limit=limit,
            expand='body.storage,version,ancestors'
        )
        return pages
    
    def fetch_page_by_id(self, page_id: str) -> Dict:
        """Fetch page by specified ID"""
        page = self.confluence.get_page_by_id(
            page_id,
            expand='body.storage,version,ancestors,space'
        )
        return page

    def fetch_space_by_key(self, space_key: str) -> Dict:
        """Fetch specified space information"""
        space = self.confluence.get_space(space_key, expand='description,homepage')
        return space

    def process_page_content(self, page: Dict) -> Dict:
        """Process page content and extract plain text"""
        content = page.get('body', {}).get('storage', {}).get('value', '')
        # Clean HTML tags
        clean_content = re.sub('<.*?>', '', content)
        
        return {
            'id': f"confluence_{page['id']}",
            'content': clean_content,
            'metadata': {
                'source': 'confluence',
                'title': page['title'],
                'space': page.get('space', {}).get('key'),
                'url': f"{self.confluence.url}/wiki{page['_links']['webui']}",
                'last_modified': page['version']['when'],
                'author': page['version']['by']['displayName']
            }
        }