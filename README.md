# AI Chatbot with Streamlit

A simple AI-powered chatbot built with Streamlit and LangChain that runs in Docker containers. This chatbot has conversation memory and can recall previous messages in your chat session.

## What This Project Does

This chatbot application:
- 🤖 Connects to AI models through OpenRouter API
- 💬 Provides a web-based chat interface
- 🧠 Remembers your conversation history
- 🐳 Runs easily with Docker (no complex setup needed)
- 🌐 Accessible through your web browser

## Prerequisites (What You Need)

Before starting, make sure you have:

1. **Docker Desktop** installed on your computer
   - For Windows: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
   - For Mac: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
   - For Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **An OpenRouter API account** (free tier available)
   - Sign up at [OpenRouter.ai](https://openrouter.ai/)
   - You'll get an API key (like a password) to use AI models

3. **A text editor** (optional but helpful)
   - Notepad on Windows, TextEdit on Mac, or any code editor like VS Code

## Quick Setup Commands

If you're comfortable with command line, here are the essential commands:

```bash
# 1. Navigate to project folder
cd chatbot

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env file with your API key
# (use your preferred text editor)

# 4. Build and run
docker-compose up --build

# 5. Open browser to http://localhost:8501
```

## Step-by-Step Setup Instructions

### Step 1: Download the Project

1. **If you have Git installed:**
   ```bash
   git clone <your-repository-url>
   cd chatbot
   ```

2. **If you don't have Git:**
   - Download the project as a ZIP file from GitHub
   - Extract it to a folder on your computer
   - Open your terminal/command prompt and navigate to the project folder

### Step 2: Set Up Your Environment Variables

Environment variables are like secret settings that tell the app how to connect to the AI service.

1. **Create a `.env` file:**
   - In the project folder, you'll find a file called `.env.example`
   - Copy this file and rename the copy to `.env` (note the dot at the beginning)
   - **Important:** This `.env` file should NOT be shared or uploaded to GitHub (it's already in .gitignore)

2. **Add your settings to the `.env` file:**
   ```
   OPENROUTER_API_KEY=your_api_key_here
   MODEL_NAME=meta-llama/llama-3.1-8b-instruct:free
   BASE_URL=https://openrouter.ai/api/v1
   ```

3. **Replace the values:**
   - `your_api_key_here`: Replace with your actual OpenRouter API key
   - `MODEL_NAME`: This uses a free model, but you can change it to other models available on OpenRouter
   - `BASE_URL`: Keep this as is (it's the OpenRouter API endpoint)

### Step 3: Verify Your Docker Installation

1. **Open your terminal/command prompt**
2. **Check if Docker is running:**
   ```bash
   docker --version
   ```
   You should see something like "Docker version 24.0.x"

3. **Check if Docker Compose is available:**
   ```bash
   docker-compose --version
   ```
   You should see something like "Docker Compose version 2.x.x"

### Step 4: Build and Run the Application

1. **Navigate to the project directory:**
   ```bash
   cd chatbot
   ```

2. **Build and start the application:**
   ```bash
   docker-compose up --build
   ```

   **What this command does:**
   - `docker-compose`: Uses Docker Compose to manage the application
   - `up`: Starts the application
   - `--build`: Builds the Docker image (first time or when you make changes)

3. **Wait for the application to start:**
   - You'll see various log messages
   - Look for a message saying the app is running on port 8501
   - **Important:** The app might take 1-2 minutes to fully start the first time

### Step 5: Access Your Chatbot

1. **Open your web browser**
2. **Go to:** `http://localhost:8501`
3. **Start chatting!**
   - Type your message in the input box at the bottom
   - Press Enter to send
   - The AI will respond with memory of your conversation

## Using the Chatbot

### Basic Usage
- Type your message in the input box at the bottom
- Press Enter or click the send button
- The AI will respond and remember your conversation

### Features
- **Conversation Memory:** The chatbot remembers what you've discussed
- **Context Management:** Check the sidebar to see conversation statistics
- **Clear Conversation:** Use the "Clear Conversation" button to start fresh

### Stopping the Application

To stop the chatbot:
1. In your terminal, press `Ctrl+C` (Windows/Linux) or `Cmd+C` (Mac)
2. Or run: `docker-compose down`

## Troubleshooting

### Common Issues

**1. "Port 8501 is already in use"**
- Another application is using port 8501
- Solution: Stop other applications or change the port in `docker-compose.yml`

**2. "API key not found" or "Authentication failed"**
- Check your `.env` file
- Make sure your OpenRouter API key is correct
- Ensure there are no extra spaces in your `.env` file

**3. "Docker command not found"**
- Docker is not installed or not running
- Install Docker Desktop and make sure it's running

**4. Application won't start**
- Check if Docker Desktop is running
- Try: `docker-compose down` then `docker-compose up --build`

**5. "Connection refused" when accessing localhost:8501**
- Wait a bit longer (app might still be starting)
- Check Docker logs: `docker-compose logs`

### Getting Help

If you encounter issues:
1. Check the Docker logs: `docker-compose logs`
2. Make sure your `.env` file is properly formatted
3. Ensure Docker Desktop is running
4. Try rebuilding: `docker-compose down` then `docker-compose up --build`

## File Structure

```
chatbot/
├── README.md           # This file
├── app.py             # Main application code
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── .env.example       # Example environment file (copy to .env)
├── .env              # Your environment variables (create from .env.example)
├── .gitignore        # Files to ignore in version control
└── .venv/            # Python virtual environment (ignored by Git)
```

## Environment Variables Explained

- **OPENROUTER_API_KEY**: Your secret key to access AI models
- **MODEL_NAME**: Which AI model to use (e.g., `meta-llama/llama-3.1-8b-instruct:free`)
- **BASE_URL**: The API endpoint (always `https://openrouter.ai/api/v1` for OpenRouter)

## Available Models

You can change the `MODEL_NAME` in your `.env` file to use different models:

**Free models:**
- `meta-llama/llama-3.1-8b-instruct:free`
- `microsoft/phi-3-medium-128k-instruct:free`
- `google/gemma-7b-it:free`

**Paid models (check OpenRouter for pricing):**
- `openai/gpt-4o-mini`
- `anthropic/claude-3-haiku`
- `google/gemini-pro`

## Security Notes

- **Never share your `.env` file** - it contains your API key
- **Never commit your `.env` file to Git** - it's already in `.gitignore`
- **Keep your API key secret** - treat it like a password
- **Regenerate your API key** if you think it's been compromised

## Need Help?

- Check the troubleshooting section above
- Look at Docker logs: `docker-compose logs`
- Visit [OpenRouter documentation](https://openrouter.ai/docs)
- Ensure your API key is valid and has credits

---

**Happy chatting!** 🚀
