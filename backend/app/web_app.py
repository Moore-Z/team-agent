#!/usr/bin/env python3
"""
🌐 Team Knowledge Agent - Web Version
FastAPI-based web server providing a Claude Code-like chat interface
This file is the core backend of the entire web application
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

# Add project root directory to Python path so we can import backend modules
# Get current file path and go up two levels to get project root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)
from backend.core.agents.qa_agent import QAAgent

# 🏗️ Create FastAPI application instance
app = FastAPI(title="Team Knowledge Agent")

# 🔗 Import and include onboarding routes
from onboarding_routes import router as onboarding_router
app.include_router(onboarding_router)

# 🤖 Initialize QA agent
# Note: This will be initialized at application startup, ensure Ollama service is running
qa_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize QA agent when application starts"""
    global qa_agent
    try:
        # Initialize QA agent using path relative to project root directory
        chroma_path = os.path.join(project_root, "data", "chroma_db")
        qa_agent = QAAgent(chroma_db_path=chroma_path, ollama_model="qwen3:4b")
        print("✅ QA Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize QA Agent: {e}")
        print("🔧 Make sure Ollama is running on http://localhost:11434")

# 📁 Configure static file service and template engine
# This line is important! It tells FastAPI to serve static files for /static/ path
# This way browsers can access /static/chat.js, /static/styles.css and other files

app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")
# Configure Jinja2 template engine for rendering HTML templates
templates = Jinja2Templates(directory="backend/app/templates")

# 📨 Define data models (for API interface data validation)
class ChatMessage(BaseModel):
    """
    Message format sent from frontend to backend
    Corresponds to the structure of JSON.stringify({ message: message }) in chat.js
    """
    message: str  # User input message content

class ChatResponse(BaseModel):
    """
    Response format returned from backend to frontend
    Corresponds to the structure of data.response in chat.js
    """
    response: str  # AI response content

# 🏠 Home route - provide chat interface
@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    """
    Triggered when user visits http://localhost:8001/
    Returns index.html template, which references chat.js
    """
    return templates.TemplateResponse("index.html", {"request": request})

# 💬 Chat API endpoint - handle user messages
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    🔄 This is the core of frontend-backend interaction!
    This function is called when chat.js sends a POST request to '/chat'

    Processing flow:
    1. Receive JSON data from chat.js {"message": "user input content"}
    2. FastAPI automatically converts JSON to ChatMessage object
    3. Process message and generate reply
    4. Return ChatResponse object, FastAPI automatically converts to JSON and returns to frontend
    """
    # Extract and clean user message
    message = chat_message.message.strip()

    # 🤖 Use real QA agent to process message
    try:
        if qa_agent is None:
            # If QA agent initialization failed, return error message
            response = "❌ AI service temporarily unavailable. Please ensure Ollama service is running."
        else:
            # Call QA agent's ask method
            result = qa_agent.ask(message)
            response = result['answer']
    except Exception as e:
        # Handle errors during the call process
        print(f"Error calling QA agent: {e}")
        response = f"Sorry, an error occurred while processing your question: {str(e)}\n\nPlease check:\n• Is Ollama service running at http://localhost:11434\n• Is the vector database properly initialized"

    # 🔙 Return formatted response
    # This ChatResponse object will be automatically converted to JSON: {"response": "reply content"}
    # chat.js will receive this JSON and extract data.response
    return ChatResponse(response=response)

# 🚀 Application startup entry point
if __name__ == "__main__":
    print("🚀 Starting Team Knowledge Agent Web Interface...")
    print("📱 Open your browser and go to: http://localhost:8001")
    # Start uvicorn server
    # host="0.0.0.0" means accept connections from any IP
    # port=8001 means listen on port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)