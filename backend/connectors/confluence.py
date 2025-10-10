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
        """获取所有可访问的空间"""
        spaces = self.confluence.get_all_spaces()
        return spaces['results']
    
    def fetch_pages(self, space_key: str, limit: int = 100) -> List[Dict]:
        """获取空间中的所有页面"""
        pages = self.confluence.get_all_pages_from_space(
            space_key, 
            start=0, 
            limit=limit,
            expand='body.storage,version,ancestors'
        )
        return pages
    
    def fetch_page_by_id(self, page_id: str) -> Dict:
        """获取指定ID的页面"""
        page = self.confluence.get_page_by_id(
            page_id,
            expand='body.storage,version,ancestors,space'
        )
        return page

    def fetch_space_by_key(self, space_key: str) -> Dict:
        """获取指定的空间信息"""
        space = self.confluence.get_space(space_key, expand='description,homepage')
        return space

    def process_page_content(self, page: Dict) -> Dict:
        """处理页面内容，提取纯文本"""
        content = page.get('body', {}).get('storage', {}).get('value', '')
        # 清理HTML标签
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