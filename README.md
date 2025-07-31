# Game Planer Chatbot

A FastAPI-based chatbot that discusses games and gaming culture using LangChain and Google's Gemini AI.

## Features

- 🤖 Intelligent game discussions and recommendations
- 🔍 Real-time search capabilities using Tavily
- 💬 Conversation memory with session management
- 🌐 RESTful API with automatic documentation
- 🎮 Specialized in gaming topics and culture

## Setup

### 1. Install Dependencies

First, activate your virtual environment (if you have one):
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

Then install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root with your API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**Getting API Keys:**
- **Google API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Tavily API Key**: Get from [Tavily](https://tavily.com/)

### 3. Run the Application

#### Option 1: Using the run script (Recommended)
```bash
python run.py
```

#### Option 2: Using uvicorn directly
```bash
uvicorn chatbot:app --reload --host 127.0.0.1 --port 8000
```

#### Option 3: Using the built-in runner
```bash
python chatbot.py
```

## Usage

### Web Interface

Once running, visit:
- **Main API**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc

### API Endpoints

#### POST /chat
Send a chat message to the bot.

**Request Body:**
```json
{
  "session_id": "unique_session_id",
  "user_input": "What are the best RPG games for beginners?"
}
```

**Response:**
```json
{
  "session_id": "unique_session_id",
  "bot_response": "Here are some great RPG games for beginners..."
}
```

### Example Usage with curl

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "my_session",
       "user_input": "Tell me about the latest gaming trends"
     }'
```

## Features

- **Conversation Memory**: The bot remembers your conversation history within each session
- **Real-time Search**: Can search for current gaming news and information
- **Gaming Expertise**: Specialized knowledge about games, genres, and gaming culture
- **Session Management**: Each session maintains its own conversation history

## Troubleshooting

### Common Issues

1. **"uvicorn not recognized"**: Make sure you've installed the requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Errors**: Ensure your `.env` file contains valid API keys

3. **Import Errors**: Make sure you're in the correct directory and virtual environment is activated

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed
2. Verify your API keys are correct
3. Ensure your virtual environment is activated
4. Check the console output for error messages

## Development

The application uses:
- **FastAPI**: Modern web framework for APIs
- **LangChain**: Framework for building LLM applications
- **Google Gemini**: AI model for natural language processing
- **Tavily**: Search tool for real-time information