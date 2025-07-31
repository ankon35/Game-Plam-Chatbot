import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.output_parser import StrOutputParser

# --- Setup ---
# 1. Load environment variables from the .env file.
# Make sure your .env file has a GOOGLE_API_KEY variable.
try:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
except Exception as e:
    print(f"Error loading API key: {e}")
    sys.exit(1)

# 2. Define the model.
# Using a specific model for consistency, as requested.
# For API key, `load_dotenv()` will handle it automatically.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 3. Set up the memory for the chatbot.
# We use ConversationBufferWindowMemory to save the last 5 interactions (k=5)
# This keeps the context from getting too long.
memory = ConversationBufferWindowMemory(
    memory_key="history",  # Key for the conversation history in the prompt.
    k=5,                   # Number of past interactions to remember.
    return_messages=True   # Returns messages as objects for the model.
)

# 4. Create a prompt template.
# This template defines the structure of the conversation for the model.
# `MessagesPlaceholder` is used to inject the chat history.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an enthusiastic and knowledgeable Game Planer. Your purpose is to talk about different types of games and the people who are passionate about them. You love discussing everything from classic board games to modern video games and esports. You can give recommendations, talk about game genres, or explain why certain games appeal to specific personalities. Always maintain a friendly, engaging, and expert tone."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

# 5. Set up the output parser.
# This simple parser just converts the model's output to a string.
output_parser = StrOutputParser()

# 6. Combine everything into a single chain.
# The LLMChain connects the model, prompt, memory, and output parser.
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    output_parser=output_parser
)

# --- Main Conversation Loop ---
print("Chatbot started! Type 'exit' to end the conversation.")
while True:
    try:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        # Invoke the chain to get a response.
        # The chain handles updating the memory automatically.
        response = chain.invoke({"input": user_input})
        
        # Print the chatbot's response.
        print("Game Planer:", response['text'])

    except Exception as e:
        print(f"An error occurred: {e}")
        # Continue the loop even on an error
        continue
