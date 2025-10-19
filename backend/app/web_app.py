#!/usr/bin/env python3
"""
🌐 团队知识代理 - Web版本
基于FastAPI的Web服务器，提供类似Claude Code的聊天界面
这个文件是整个Web应用的后端核心
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
import uvicorn
import sys
import os

# 添加项目根目录到Python路径，这样就可以导入backend模块
# 获取当前文件的路径，向上两级得到项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)
from backend.core.agents.qa_agent import QAAgent

# 🏗️ 创建FastAPI应用实例
app = FastAPI(title="Team Knowledge Agent")

# 🤖 初始化QA代理
# 注意：这会在应用启动时初始化，确保Ollama服务正在运行
qa_agent = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化QA代理"""
    global qa_agent
    try:
        # 初始化QA代理，使用相对于项目根目录的路径
        chroma_path = os.path.join(project_root, "data", "chroma_db")
        qa_agent = QAAgent(chroma_db_path=chroma_path, ollama_model="qwen3:4b")
        print("✅ QA Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize QA Agent: {e}")
        print("🔧 Make sure Ollama is running on http://localhost:11434")

# 📁 配置静态文件服务和模板引擎
# 这一行很重要！它告诉FastAPI为 /static/ 路径提供静态文件服务
# 这样浏览器就可以访问 /static/chat.js, /static/styles.css 等文件

app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")
# 配置Jinja2模板引擎，用于渲染HTML模板
templates = Jinja2Templates(directory="backend/app/templates")

# 📨 定义数据模型（用于API接口的数据验证）
class ChatMessage(BaseModel):
    """
    前端发送给后端的消息格式
    对应 chat.js 中 JSON.stringify({ message: message }) 的结构
    """
    message: str  # 用户输入的消息内容

class ChatResponse(BaseModel):
    """
    后端返回给前端的响应格式
    对应 chat.js 中 data.response 的结构
    """
    response: str  # AI的回复内容

# 🏠 主页路由 - 提供聊天界面
@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    """
    当用户访问 http://localhost:8001/ 时触发
    返回 index.html 模板，模板中会引用 chat.js
    """
    return templates.TemplateResponse("index.html", {"request": request})

# 💬 聊天API端点 - 处理用户消息
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    🔄 这是前后端交互的核心！
    当 chat.js 发送 POST 请求到 '/chat' 时，这个函数会被调用

    处理流程：
    1. 接收来自 chat.js 的 JSON 数据 {"message": "用户输入的内容"}
    2. FastAPI自动将JSON转换为ChatMessage对象
    3. 处理消息并生成回复
    4. 返回ChatResponse对象，FastAPI自动转换为JSON返回给前端
    """
    # 提取并清理用户消息
    message = chat_message.message.strip()

    # 🤖 使用真正的QA代理处理消息
    try:
        if qa_agent is None:
            # 如果QA代理初始化失败，返回错误信息
            response = "❌ AI服务暂时不可用。请确保Ollama服务正在运行。"
        else:
            # 调用QA代理的ask方法
            result = qa_agent.ask(message)
            response = result['answer']
    except Exception as e:
        # 处理调用过程中的错误
        print(f"Error calling QA agent: {e}")
        response = f"抱歉，处理您的问题时出现了错误：{str(e)}\n\n请检查：\n• Ollama服务是否运行在 http://localhost:11434\n• 向量数据库是否已正确初始化"

    # 🔙 返回格式化的响应
    # 这个ChatResponse对象会被自动转换为JSON: {"response": "回复内容"}
    # chat.js会接收到这个JSON并提取 data.response
    return ChatResponse(response=response)

# 🚀 应用启动入口
if __name__ == "__main__":
    print("🚀 Starting Team Knowledge Agent Web Interface...")
    print("📱 Open your browser and go to: http://localhost:8001")
    # 启动uvicorn服务器
    # host="0.0.0.0" 表示接受来自任何IP的连接
    # port=8001 表示监听8001端口
    uvicorn.run(app, host="0.0.0.0", port=8001)