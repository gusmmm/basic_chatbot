from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import streamlit as st
import os

# Configure Streamlit page
st.set_page_config(page_title="AI Chatbot", layout="wide")

# Initialize environment variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME")  # Default model from env
BASE_URL = os.environ.get("BASE_URL")

# Function to load available models from MODELS.txt
@st.cache_data
def load_available_models():
    """Load available models from MODELS.txt file"""
    try:
        models = []
        with open("MODELS.txt", "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    models.append(line)
        return models
    except FileNotFoundError:
        st.error("MODELS.txt file not found!")
        return []
    except Exception as e:
        st.error(f"Error reading MODELS.txt: {str(e)}")
        return []

# Validate environment variables
def validate_environment():
    """Validate that all required environment variables are set"""
    missing_vars = []

    if not OPENROUTER_API_KEY:
        missing_vars.append("OPENROUTER_API_KEY")
    if not BASE_URL:
        missing_vars.append("BASE_URL")

    if missing_vars:
        return False, missing_vars
    return True, []

# Check environment variables on startup
env_valid, missing_vars = validate_environment()

if not env_valid:
    st.error("⚠️ Missing required environment variables:")
    for var in missing_vars:
        st.error(f"• {var}")
    st.info("""
    Please set the following environment variables:

    **For local development:**
    ```bash
    export OPENROUTER_API_KEY="your-api-key-here"
    export BASE_URL="https://openrouter.ai/api/v1"
    ```

    **For Docker:**
    Set them in your docker-compose.yml or pass them with -e flags.
    """)
    st.stop()

# Load available models
available_models = load_available_models()

if not available_models:
    st.error("No models available! Please check MODELS.txt file.")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    # Use MODEL_NAME from env as default, or first available model
    default_model = MODEL_NAME if MODEL_NAME in available_models else available_models[0]
    st.session_state.selected_model = default_model

# Initialize the LLM with selected model
@st.cache_resource
def get_llm(model_name):
    """Initialize ChatOpenAI with specified model"""
    try:
        return ChatOpenAI(
            model=model_name,
            api_key=OPENROUTER_API_KEY,
            base_url=BASE_URL,
        )
    except Exception as e:
        st.error(f"Failed to initialize ChatOpenAI with model {model_name}: {str(e)}")
        st.info("Please check your environment variables and API key.")
        return None

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


# --- Tabs UI ---
tab1, tab2 = st.tabs(["Chatbot", "PDF monger"])

# --- Chatbot Tab ---
with tab1:
    st.title("AI Chatbot - Multi-Model")

    # Model selection in the main area (top of chat)
    col1, col2, col3 = st.columns([2, 3, 1])

    with col1:
        st.subheader("🤖 Current Model:")

    with col2:
        # Model selection dropdown
        selected_model = st.selectbox(
            "Choose AI Model:",
            options=available_models,
            index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
            key="model_selector"
        )

        # Handle model change
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            # Clear the LLM cache when model changes
            get_llm.clear()
            st.success(f"✅ Switched to model: {selected_model}")
            st.rerun()

    with col3:
        if st.button("🔄 Refresh Models"):
            load_available_models.clear()
            st.rerun()

    # Display current model info
    st.info(f"**Active Model:** `{st.session_state.selected_model}`")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Show which model was used for assistant messages
            if message["role"] == "assistant" and "model_used" in message:
                st.caption(f"🤖 Generated by: {message['model_used']}")

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
                my_llm = get_llm(st.session_state.selected_model)

                if my_llm is None:
                    error_msg = "Failed to initialize the AI model. Please check your configuration."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "model_used": st.session_state.selected_model
                    })
                    st.stop()

                # Build context from previous messages
                context = build_context(max_messages=20)

                # Add current user message to context
                context.append(HumanMessage(content=prompt))

                # Show context and model info
                st.caption(f"🤖 Using: {st.session_state.selected_model} | Context: {len(context)-1} messages")

                # Get response with full context
                with st.spinner(f"Thinking with {st.session_state.selected_model}..."):
                    response = my_llm.invoke(context)

                st.markdown(response.content)

                # Add assistant response to chat history with model info
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.content,
                    "model_used": st.session_state.selected_model
                })

            except Exception as e:
                error_msg = f"Erro ao processar a mensagem: {str(e)}"
                st.error(error_msg)
                st.error("💡 **Troubleshooting tips:**")
                st.error("• Check if your API key is valid")
                st.error("• Verify the model name is correct")
                st.error("• Ensure the base URL is accessible")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "model_used": st.session_state.selected_model
                })

# --- PDF Monger Tab ---
with tab2:
    import PyPDF2

    st.title("PDF Monger")

    # Sidebar for PDF upload and info
    with st.sidebar:
        st.header("📄 PDF Upload & Info")
        uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"], key="pdf_uploader")

        if uploaded_pdf is not None:
            # Read PDF info
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
                num_pages = len(pdf_reader.pages)
                file_name = uploaded_pdf.name
                file_size = uploaded_pdf.size if hasattr(uploaded_pdf, 'size') else None

                st.success(f"**File:** {file_name}")
                if file_size:
                    st.info(f"**Size:** {file_size/1024:.2f} KB")
                st.info(f"**Pages:** {num_pages}")
            except Exception as e:
                st.error(f"Failed to read PDF: {str(e)}")

    # Main area: PDF viewer
    if 'uploaded_pdf' not in st.session_state or st.session_state.uploaded_pdf != uploaded_pdf:
        st.session_state.uploaded_pdf = uploaded_pdf
        st.session_state.pdf_page = 0

    if uploaded_pdf is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            num_pages = len(pdf_reader.pages)

            # Page selector
            page_num = st.number_input("Page", min_value=1, max_value=num_pages, value=st.session_state.pdf_page+1, key="pdf_page_selector")
            st.session_state.pdf_page = page_num - 1

            # Display page text
            page = pdf_reader.pages[st.session_state.pdf_page]
            text = page.extract_text() or "[No extractable text on this page]"
            st.text_area(f"Page {page_num} Text", text, height=400)
        except Exception as e:
            st.error(f"Error displaying PDF: {str(e)}")

# Sidebar for management
with st.sidebar:
    st.header("🛠️ Chat Management")

    # Show total messages in memory
    st.metric("Total Messages", len(st.session_state.messages))

    # Button to clear conversation history
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    # Model information section
    st.subheader("🤖 Model Information")
    st.info(f"**Current:** {st.session_state.selected_model}")
    st.info(f"**Available Models:** {len(available_models)}")

    # Show all available models
    with st.expander("📋 All Available Models"):
        for i, model in enumerate(available_models, 1):
            if model == st.session_state.selected_model:
                st.write(f"**{i}. {model}** ✅")
            else:
                st.write(f"{i}. {model}")

    # Configuration status
    st.subheader("⚙️ Configuration Status")
    if env_valid:
        st.success("✅ Environment variables configured")
    else:
        st.error("❌ Missing environment variables")

    if env_valid:
        st.info(f"**API:** {BASE_URL}")
        st.info(f"**Models:** {len(available_models)} available")

    # Show recent context summary
    if st.session_state.messages:
        st.subheader("💬 Recent Context")
        context = build_context(max_messages=5)  # Show last 5 for preview
        for i, msg in enumerate(context[1:], 1):  # Skip system message
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            st.text(f"{role}: {msg.content[:50]}...")

    # Model usage statistics
    if st.session_state.messages:
        st.subheader("📊 Model Usage")
        model_usage = {}
        for msg in st.session_state.messages:
            if msg["role"] == "assistant" and "model_used" in msg:
                model = msg["model_used"]
                model_usage[model] = model_usage.get(model, 0) + 1

        for model, count in model_usage.items():
            st.write(f"**{model}:** {count} responses")
