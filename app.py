from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import streamlit as st
import os

# Configure Streamlit page
st.set_page_config(page_title="AI Chatbot", layout="wide")

# Initialize environment variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME")
BASE_URL = os.environ.get("BASE_URL")

# Initialize the LLM
@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENROUTER_API_KEY,
        base_url=BASE_URL,
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to build context from previous messages
def build_context(max_messages=10):
    """Build context from previous messages with optional length limit"""
    context = []

    # Add system message for context
    context.append(SystemMessage(content="You are a helpful AI assistant. Use the conversation history to provide contextual responses."))

    # Get recent messages (limit to max_messages to avoid token limits)
    recent_messages = st.session_state.messages[-max_messages:] if len(st.session_state.messages) > max_messages else st.session_state.messages

    # Add previous messages as context
    for message in recent_messages:
        if message["role"] == "user":
            context.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            context.append(AIMessage(content=message["content"]))

    return context

# Display title
st.title("App com Streamlit")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Digita a tua mensagem, cucatano..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        try:
            my_llm = get_llm()

            # Build context from previous messages (local variable)
            context = build_context(max_messages=20)  # Limit to last 20 messages

            # Add current user message to context
            context.append(HumanMessage(content=prompt))

            # Debug: Show context length (optional - remove in production)
            st.caption(f"Context includes {len(context)-1} previous messages")

            # Get response with full context
            response = my_llm.invoke(context)
            st.markdown(response.content)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response.content})
        except Exception as e:
            error_msg = f"Erro ao processar a mensagem: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar for context management
with st.sidebar:
    st.header("Context Management")

    # Show total messages in memory
    st.metric("Total Messages", len(st.session_state.messages))

    # Button to clear conversation history
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    # Show recent context summary
    if st.session_state.messages:
        st.subheader("Recent Context")
        context = build_context(max_messages=5)  # Show last 5 for preview
        for i, msg in enumerate(context[1:], 1):  # Skip system message
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            st.text(f"{role}: {msg.content[:50]}...")
