import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 强制使用绝对路径设置项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 强制使用绝对路径加载 .env 文件
load_dotenv(project_root / '.env', override=True)

from backend.connectors.confluence import ConfluenceConnector
import json
from typing import List, Dict

# Load environment variables
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
USERNAME = os.getenv('CONFLUENCE_USERNAME')
API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')
PERSONAL_SPACE_KEY = os.getenv('CONFLUENCE_PERSONAL_SPACE_KEY')

class FormConfluenceDataToPersist(ConfluenceConnector):
    def __init__(self, url: str = None, username: str = None, api_token: str = None):
        # 使用传入的参数或环境变量
        confluence_url = url or CONFLUENCE_URL
        confluence_username = username or USERNAME
        confluence_api_token = api_token or API_TOKEN

        # 调试信息：检查凭据
        if not confluence_url:
            raise ValueError("Confluence URL 未配置")
        if not confluence_username:
            raise ValueError("Confluence 用户名未配置")
        if not confluence_api_token:
            raise ValueError("Confluence API Token 未配置")

        # 调用父类的初始化方法
        super().__init__(confluence_url, confluence_username, confluence_api_token)

        self.personal_space_key = PERSONAL_SPACE_KEY

    def fetch_personal_space_pages(self, limit: int = 100) -> List[Dict]:
        """获取个人空间的所有页面"""
        if not self.personal_space_key:
            raise ValueError("Personal space key not configured")
        return self.fetch_pages(self.personal_space_key, limit)

    def process_and_save_pages_to_json(self, space_key: str = None, output_file: str = "confluence_data.json") -> str:
        """处理页面并保存为JSON格式"""
        target_space = space_key or self.personal_space_key
        if not target_space:
            raise ValueError("No space key provided and personal space key not configured")

        # 获取页面
        pages = self.fetch_pages(target_space)

        # 处理每个页面
        processed_pages = []
        for page in pages:
            processed_page = self.process_page_content(page)
            processed_pages.append(processed_page)

        # 保存到JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_pages, f, ensure_ascii=False, indent=2)

        return f"Successfully saved {len(processed_pages)} pages to {output_file}"


# 测试代码
if __name__ == "__main__":
    def test_confluence_connector():
        """测试 Confluence 连接器功能"""
        try:
            print("🚀 开始测试 Confluence 连接器...")

            # 添加环境诊断
            print(f"\n🔍 环境诊断:")
            print(f"   📁 工作目录: {os.getcwd()}")
            print(f"   📄 脚本位置: {__file__}")
            print(f"   📁 项目根目录: {project_root}")
            print(f"   📄 .env 文件: {project_root / '.env'}")
            print(f"   🔧 URL配置: {'已设置' if CONFLUENCE_URL else '未设置'}")
            print(f"   👤 用户名配置: {'已设置' if USERNAME else '未设置'}")
            print(f"   🔑 API Token: {'已设置' if API_TOKEN else '未设置'}")
            print(f"   🏠 个人空间: {'已设置' if PERSONAL_SPACE_KEY else '未设置'}")

            # 创建连接器实例
            connector = FormConfluenceDataToPersist()
            print("✅ 连接器初始化成功")

            # 测试获取空间列表
            print("\n📂 测试获取空间列表...")
            spaces = connector.fetch_spaces()
            print(f"✅ 找到 {len(spaces)} 个空间")
            for space in spaces[:3]:  # 只显示前3个
                print(f"   - {space.get('name')} ({space.get('key')})")

            # 测试获取个人空间信息
            if connector.personal_space_key:
                print(f"\n🏠 测试获取个人空间信息: {connector.personal_space_key}")
                try:
                    personal_space = connector.fetch_space_by_key(connector.personal_space_key)
                    print(f"✅ 个人空间: {personal_space.get('name')}")
                except Exception as e:
                    print(f"⚠️ 获取个人空间失败: {e}")

                # 测试获取个人空间页面
                print(f"\n📄 测试获取个人空间页面...")
                try:
                    pages = connector.fetch_personal_space_pages(limit=5)
                    print(f"✅ 找到 {len(pages)} 个页面")
                    for page in pages:
                        print(f"   - {page.get('title')}")
                except Exception as e:
                    print(f"⚠️ 获取页面失败: {e}")
            else:
                print("⚠️ 未配置个人空间密钥，跳过个人空间测试")

            # 测试处理和保存数据（如果有页面的话）
            if connector.personal_space_key:
                print(f"\n💾 测试保存数据到 JSON...")
                try:
                    result = connector.process_and_save_pages_to_json(
                        output_file="data/jason/test_confluence_data.json"
                    )
                    print(f"✅ {result}")
                except Exception as e:
                    print(f"⚠️ 保存数据失败: {e}")

            print("\n🎉 测试完成！")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            print("请检查环境变量配置:")
            print("- CONFLUENCE_URL")
            print("- CONFLUENCE_USERNAME")
            print("- CONFLUENCE_API_TOKEN")
            print("- CCONFLUENCE_PERSONAL_SPACE_KEY")

    def test_environment_variables():
        """检查环境变量配置"""
        print("🔧 检查环境变量配置...")

        required_vars = {
            'CONFLUENCE_URL': CONFLUENCE_URL,
            'CONFLUENCE_USERNAME': USERNAME,
            'CONFLUENCE_API_TOKEN': API_TOKEN,
            'CCONFLUENCE_PERSONAL_SPACE_KEY': PERSONAL_SPACE_KEY
        }

        missing_vars = []
        for var_name, var_value in required_vars.items():
            if var_value:
                print(f"✅ {var_name}: 已配置")
            else:
                print(f"❌ {var_name}: 未配置")
                missing_vars.append(var_name)

        if missing_vars:
            print(f"\n⚠️ 缺少环境变量: {', '.join(missing_vars)}")
            print("请在 .env 文件中配置这些变量")
            return False
        else:
            print("\n✅ 所有环境变量都已配置")
            return True

    # 运行测试
    print("=" * 50)
    print("Confluence 连接器测试")
    print("=" * 50)

    # 首先检查环境变量
    if test_environment_variables():
        print("\n" + "=" * 50)
        # 然后运行功能测试
        test_confluence_connector()
    else:
        print("\n❌ 环境变量配置不完整，跳过功能测试")