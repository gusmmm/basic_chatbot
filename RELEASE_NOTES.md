# Release Notes

## Version 0.1 (July 18, 2025)

### 🎉 Initial Release

This is the first stable release of the AI Chatbot application. This version provides a solid foundation for AI-powered conversations with a user-friendly interface.

### ✨ Features

- **Web-based Chat Interface**: Clean and intuitive Streamlit-based UI for chatting with AI
- **Conversation Memory**: Chatbot remembers previous messages in your conversation session
- **OpenRouter Integration**: Seamless integration with OpenRouter API for access to multiple AI models
- **Docker Support**: Complete containerization for easy deployment and consistent environments
- **Context Management**: Intelligent context handling with configurable message limits to optimize performance
- **Real-time Chat**: Live chat interface with message history display
- **Sidebar Controls**: Context management panel showing conversation statistics and clear conversation option

### 🔧 Technical Highlights

- **LangChain Integration**: Built on LangChain for robust AI model interactions
- **Session State Management**: Persistent conversation history during user sessions
- **Environment Configuration**: Secure API key management through environment variables
- **Error Handling**: Comprehensive error handling with user-friendly error messages
- **Performance Optimization**: Cached LLM initialization and context length management

### 🐳 Docker Configuration

- **Multi-stage Build**: Optimized Docker image with Python 3.12 slim base
- **Environment Variables**: Secure configuration through Docker Compose
- **Health Checks**: Built-in health monitoring for container reliability
- **Port Mapping**: Standard port 8501 for web interface access

### 📖 Documentation

- **Comprehensive README**: Detailed setup instructions for users of all technical levels
- **Environment Template**: `.env.example` file with clear configuration guidance
- **Troubleshooting Guide**: Common issues and solutions included
- **Security Best Practices**: Guidelines for API key protection and secure deployment

### 🎯 Supported Models

This release supports all OpenRouter-compatible models including:
- **Free Models**: Llama 3.1, Phi-3, Gemma 7B
- **Premium Models**: GPT-4o-mini, Claude 3 Haiku, Gemini Pro
- **Easy Model Switching**: Change models via environment variable configuration

### 🔒 Security

- **API Key Protection**: Secure environment variable handling
- **Git Ignore Configuration**: Prevents accidental exposure of sensitive data
- **No Hardcoded Credentials**: All sensitive information externalized

### 🚀 Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and add your OpenRouter API key
3. Run `docker-compose up --build`
4. Access the chatbot at `http://localhost:8501`

### 🐛 Known Issues

- Context length is limited to 20 messages to prevent token overflow
- Conversation history is lost when the container restarts
- No persistent storage for chat history across sessions

### 📝 Requirements

- Docker Desktop installed and running
- OpenRouter API account and key
- Web browser for accessing the interface

### 🤝 Contributing

This is an open-source project. Feel free to submit issues, feature requests, or pull requests.

---

**Full Changelog**: Initial release - no previous versions to compare

**Docker Image**: Built from Python 3.12-slim with optimized dependencies