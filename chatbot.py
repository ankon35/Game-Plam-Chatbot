import os
import sys
from dotenv import load_dotenv
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.schema.output_parser import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_tavily import TavilySearch

# --- Application Setup ---
# Load environment variables.
try:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or not tavily_api_key:
        raise ValueError("API keys not found in environment variables.")
except Exception as e:
    print(f"Error loading API keys: {e}")
    sys.exit(1)

# Initialize FastAPI application
app = FastAPI(
    title="Game Planer Chatbot API",
    description="An API for a chatbot that talks about games and gamers.",
    version="1.0.0",
)

# Define the model, agent, and tools globally so they are initialized once.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")
tavily_search = TavilySearch(max_results=5)
tools = [tavily_search]

# Define the prompt template for the agent.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an enthusiastic and knowledgeable Game Planer. Your purpose is to talk about different types of games and the people who are passionate about them. You love discussing everything from classic board games to modern video games and esports. You can give recommendations, talk about game genres, or explain why certain games appeal to specific personalities. You must use the search tool to find up-to-date information when asked about current events, new game releases, or facts you don't know."),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent and executor.
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# In-memory store for chat history.
# This will hold the conversation history for different sessions.
store = {}
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Returns the chat history for a given session ID, creating a new one if it doesn't exist."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# The main runnable with message history.
with_message_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# --- API Models ---
class ChatbotRequest(BaseModel):
    """Pydantic model for the incoming chat request payload."""
    session_id: str
    user_input: str

class ChatbotResponse(BaseModel):
    """Pydantic model for the outgoing chat response payload."""
    session_id: str
    bot_response: str
    
# --- API Endpoints ---
@app.get("/", summary="Root Endpoint")
async def root():
    """A simple root endpoint to check if the API is running."""
    return {"message": "Welcome to the Game Planer Chatbot API!"}

@app.post("/chat", response_model=ChatbotResponse, summary="Chat Endpoint")
async def chat_endpoint(request: ChatbotRequest):
    """
    Main endpoint for interacting with the chatbot.
    
    It takes a session_id and user_input, processes the request with the LangChain agent,
    and returns the chatbot's response.
    """
    try:
        # Invoke the agent with the user's input and session ID
        response = await with_message_history.ainvoke(
            {"input": request.user_input},
            config={"configurable": {"session_id": request.session_id}}
        )
        
        # The agent executor's response is in the 'output' key.
        bot_output = response.get("output")
        if not bot_output:
            raise HTTPException(status_code=500, detail="The chatbot did not return a response.")
            
        return ChatbotResponse(session_id=request.session_id, bot_response=bot_output)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting Game Planer Chatbot API...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API documentation will be available at: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
