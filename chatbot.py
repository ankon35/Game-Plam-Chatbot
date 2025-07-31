import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# Updated import for the new memory class
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.schema.output_parser import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_tavily import TavilySearch
from langchain_core.tools import Tool

# --- Setup ---
# 1. Load environment variables from the .env file.
# Make sure your .env file has GOOGLE_API_KEY and TAVILY_API_KEY variables.
try:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables.")
except Exception as e:
    print(f"Error loading API keys: {e}")
    sys.exit(1)

# 2. Define the model. The model must support tool calling.
# `gemini-2.5-flash-preview-05-20` is a good choice for this.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")

# 3. Create the Tavily search tool.
# This tool will be available for the agent to use.
tavily_search = TavilySearch(max_results=5)
tools = [tavily_search]

# 4. Create a prompt template for the agent.
# The system prompt now instructs the agent on when to use the search tool.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an enthusiastic and knowledgeable Game Planer. Your purpose is to talk about different types of games and the people who are passionate about them. You love discussing everything from classic board games to modern video games and esports. You can give recommendations, talk about game genres, or explain why certain games appeal to specific personalities. You must use the search tool to find up-to-date information when asked about current events, new game releases, or facts you don't know."),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 5. Create the agent with the LLM, tools, and prompt.
agent = create_tool_calling_agent(llm, tools, prompt)

# 6. Create the AgentExecutor to run the agent.
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True, # Set verbose to True to see the agent's thought process
    handle_parsing_errors=True
)

# 7. Define a function to get or create a session's history.
# The recommended way to handle this is with InMemoryChatMessageHistory
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 8. Add message history to the agent executor.
with_message_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# --- Main Conversation Loop ---
print("Chatbot started! Type 'exit' to end the conversation.")
session_id = "my-chat-session-id"

while True:
    try:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        response = with_message_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        
        # The agent executor's response will be in the 'output' key.
        print("Chatbot:", response["output"])

    except Exception as e:
        print(f"An error occurred: {e}")
        continue
