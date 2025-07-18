# 🤖 AI Chatbot v0.1 - Initial Release

## What's New

This is the first stable release of our AI-powered chatbot! 🎉

### ✨ Key Features

- **💬 Interactive Chat Interface** - Clean web-based chat powered by Streamlit
- **🧠 Conversation Memory** - Remembers your chat history during the session
- **🔌 OpenRouter Integration** - Connect to multiple AI models (free & premium)
- **🐳 Docker Ready** - One-command setup with Docker Compose
- **⚙️ Easy Configuration** - Simple environment variable setup
- **📊 Context Management** - Smart conversation tracking with sidebar controls

### 🚀 Quick Start

1. Clone the repo
2. Copy `.env.example` to `.env` and add your OpenRouter API key
3. Run `docker-compose up --build`
4. Open `http://localhost:8501` and start chatting!

### 🎯 Supported Models

- **Free**: Llama 3.1, Phi-3, Gemma 7B
- **Premium**: GPT-4o-mini, Claude 3 Haiku, Gemini Pro

### 📋 What's Included

- Complete Docker setup for easy deployment
- Comprehensive documentation for beginners
- Security best practices with `.gitignore` protection
- Error handling and troubleshooting guides
- Environment template for quick configuration

### 🔒 Security

- API keys protected via environment variables
- No sensitive data committed to repository
- Secure Docker container configuration

### 🐛 Known Limitations

- Conversation history resets when container restarts
- Context limited to 20 messages to prevent token overflow
- No persistent storage across sessions

---

**Perfect for**: Developers wanting to quickly deploy an AI chatbot, learning Docker + AI integration, or building a foundation for more complex chatbot projects.

**Next up**: Planning v0.2 with persistent storage and additional features!