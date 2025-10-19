// ================================
// 前端聊天界面的JavaScript逻辑
// 这个文件负责处理用户界面交互和与后端的通信
// ================================

// 📱 获取页面中的重要DOM元素（HTML元素的引用）
// 这些元素在 index.html 中定义
const messagesContainer = document.getElementById('messages');   // 聊天消息容器
const messageInput = document.getElementById('messageInput');     // 用户输入框
const sendButton = document.getElementById('sendButton');         // 发送按钮
const chatForm = document.getElementById('chatForm');             // 表单容器
const thinking = document.getElementById('thinking');             // "正在思考..."提示

// 📝 添加消息到聊天界面的函数
// 参数：content = 消息内容，isUser = 是否为用户消息（默认false，即AI消息）
function addMessage(content, isUser = false) {
    // 如果存在欢迎消息，先移除它（用户发送第一条消息时）
    const welcome = messagesContainer.querySelector('.welcome');
    if (welcome) {
        welcome.remove();
    }

    // 创建新的消息div元素
    const messageDiv = document.createElement('div');
    // 设置CSS类名：如果是用户消息就加'user'类，否则加'assistant'类
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    // 设置消息文本内容
    messageDiv.textContent = content;
    // 将消息添加到消息容器中
    messagesContainer.appendChild(messageDiv);
    // 自动滚动到最底部，显示最新消息
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 💭 显示"正在思考..."动画
function showThinking() {
    thinking.classList.add('show');  // 添加'show'类来显示思考动画
    messagesContainer.scrollTop = messagesContainer.scrollHeight;  // 滚动到底部
}

// 🙈 隐藏"正在思考..."动画
function hideThinking() {
    thinking.classList.remove('show');  // 移除'show'类来隐藏思考动画
}

// 🔄 设置界面的加载状态
// 参数：loading = true时禁用输入，false时启用输入
function setLoading(loading) {
    sendButton.disabled = loading;     // 禁用/启用发送按钮
    messageInput.disabled = loading;   // 禁用/启用输入框
    if (loading) {
        showThinking();   // 显示思考动画
    } else {
        hideThinking();   // 隐藏思考动画
    }
}

// 🌐 发送消息到后端服务器的异步函数
// 这里使用了 fetch API 进行网络请求
async function sendMessage(message) {
    try {
        // 发送POST请求到 '/chat' 端点（这里会连接到 web_app.py 的 @app.post("/chat") 路由）
        const response = await fetch('/chat', {
            method: 'POST',                           // HTTP方法：POST
            headers: {
                'Content-Type': 'application/json',   // 告诉服务器我们发送的是JSON数据
            },
            body: JSON.stringify({ message: message }) // 将消息转换为JSON字符串发送
        });

        // 检查HTTP响应是否成功
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // 将响应解析为JSON对象
        const data = await response.json();
        // 返回服务器返回的response字段（对应web_app.py中ChatResponse.response）
        return data.response;
    } catch (error) {
        // 如果网络请求失败，打印错误并返回友好的错误消息
        console.error('Error:', error);
        return 'Sorry, I encountered an error. Please try again.';
    }
}

// 📤 监听表单提交事件（当用户点击发送按钮或按回车时触发）
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();  // 阻止表单的默认提交行为（阻止页面刷新）

    // 获取用户输入的消息并去除首尾空格
    const message = messageInput.value.trim();
    if (!message) return;  // 如果消息为空，不做任何操作

    // 1. 立即显示用户的消息（第二个参数true表示这是用户消息）
    addMessage(message, true);
    // 2. 清空输入框
    messageInput.value = '';
    // 3. 设置加载状态（禁用输入，显示思考动画）
    setLoading(true);

    // 4. 发送消息到服务器并等待响应
    const response = await sendMessage(message);
    // 5. 取消加载状态（启用输入，隐藏思考动画）
    setLoading(false);
    // 6. 显示AI的回复（第二个参数默认为false，表示这是AI消息）
    addMessage(response);
});

// ⌨️ 监听输入框的键盘事件
messageInput.addEventListener('keydown', (e) => {
    // 如果用户按下回车键且没有同时按Shift键
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();  // 阻止默认的换行行为
        // 手动触发表单提交事件（相当于点击发送按钮）
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// 🎯 页面加载完成后自动聚焦到输入框
// 这样用户打开页面就可以直接开始打字
window.addEventListener('load', () => {
    messageInput.focus();
});