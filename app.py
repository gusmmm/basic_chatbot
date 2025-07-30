from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

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

# Sidebar for management (outside tabs for consistency)
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

    # Chat input - moved to bottom to ensure proper positioning
    if prompt := st.chat_input("Digita a tua mensagem, cucatano..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get AI response
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
                st.rerun()

            # Build context from previous messages
            context = build_context(max_messages=20)

            # Add current user message to context
            context.append(HumanMessage(content=prompt))

            # Get response with full context
            with st.spinner(f"Thinking with {st.session_state.selected_model}..."):
                response = my_llm.invoke(context)

            # Add assistant response to chat history with model info
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.content,
                "model_used": st.session_state.selected_model
            })
            
            # Rerun to display the new messages
            st.rerun()

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
            st.rerun()

# --- PDF Monger Tab ---
with tab2:
    from pdf_processor.main_pdf_processor import PDFProcessor
    import tempfile
    import json

    st.title("PDF Monger - Advanced Processing")

    # Initialize session state for PDF
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = None
    if 'uploaded_pdf_name' not in st.session_state:
        st.session_state.uploaded_pdf_name = None

    # Create columns for PDF upload and results
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📄 PDF Upload & Processing")
        uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"], key="pdf_uploader")
        
        if uploaded_pdf is not None:
            # Display basic file info
            file_name = uploaded_pdf.name
            file_size = uploaded_pdf.size if hasattr(uploaded_pdf, 'size') else None
            
            st.success(f"**File:** {file_name}")
            if file_size:
                st.info(f"**Size:** {file_size/1024:.2f} KB")
            
            # Processing button
            if st.button("🚀 Process PDF with Docling", type="primary"):
                with st.spinner("Processing PDF with Docling... This may take a few minutes."):
                    try:
                        # Save uploaded file to temporary location
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_pdf.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Process the PDF
                        results = st.session_state.pdf_processor.process_pdf(
                            tmp_file_path, 
                            output_base_dir="output"
                        )
                        
                        # Clean up temporary file
                        import os
                        os.unlink(tmp_file_path)
                        
                        # Store results in session state
                        st.session_state.processing_results = results
                        st.session_state.uploaded_pdf_name = file_name
                        
                        st.success(f"✅ PDF processed successfully in {results['processing_time']:.2f} seconds!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing PDF: {str(e)}")
            
            # Show processing status if available
            if st.session_state.processing_results and st.session_state.uploaded_pdf_name == file_name:
                results = st.session_state.processing_results
                st.subheader("📊 Processing Results")
                
                col_metrics1, col_metrics2 = st.columns(2)
                with col_metrics1:
                    st.metric("Pages", results['page_count'])
                    st.metric("Tables", results['table_count'])
                with col_metrics2:
                    st.metric("Pictures", results['picture_count'])
                    st.metric("Time (s)", f"{results['processing_time']:.2f}")
                
                # Output location
                st.info(f"📁 **Output saved to:** `{results['output_dir']}`")

    with col2:
        st.subheader("📖 Processing Results & Viewer")
        
        if st.session_state.processing_results and uploaded_pdf is not None:
            results = st.session_state.processing_results
            
            # Create tabs for different output types
            view_tab1, view_tab2, view_tab3, view_tab4 = st.tabs(["📄 Text", "🖼️ Images", "📊 Files", "🔍 Raw Data"])
            
            with view_tab1:
                st.subheader("Extracted Text Content")
                try:
                    # Try to load the text file
                    text_file = results.get('text_file')
                    if text_file and os.path.exists(text_file):
                        with open(text_file, 'r', encoding='utf-8') as f:
                            text_content = f.read()
                        st.text_area("Document Text", text_content, height=400)
                    else:
                        st.info("Text file not found. Try processing the PDF again.")
                except Exception as e:
                    st.error(f"Error loading text content: {str(e)}")
            
            with view_tab2:
                st.subheader("Extracted Images")
                
                # Create sub-tabs for different image types
                img_tab1, img_tab2, img_tab3 = st.tabs(["📄 Pages", "📊 Tables", "🖼️ Pictures"])
                
                with img_tab1:
                    st.write("**Page Images:**")
                    if results['page_images']:
                        # Show page selector for navigation
                        if len(results['page_images']) > 1:
                            page_to_show = st.selectbox(
                                "Select page to view:",
                                range(1, len(results['page_images']) + 1),
                                format_func=lambda x: f"Page {x}",
                                key="page_selector"
                            ) - 1
                        else:
                            page_to_show = 0
                        
                        # Display selected page
                        if page_to_show < len(results['page_images']):
                            img_path = results['page_images'][page_to_show]
                            if os.path.exists(img_path):
                                st.image(img_path, caption=f"Page {page_to_show + 1}", use_container_width=True)
                            else:
                                st.error(f"Page image not found: {img_path}")
                        
                        # Show navigation info
                        st.info(f"📄 Total pages: {len(results['page_images'])}")
                        
                        # Show thumbnails for quick navigation (first 5 pages)
                        if len(results['page_images']) > 1:
                            st.write("**Page Thumbnails:**")
                            cols = st.columns(min(5, len(results['page_images'])))
                            for i, img_path in enumerate(results['page_images'][:5]):
                                if os.path.exists(img_path):
                                    with cols[i]:
                                        st.image(img_path, caption=f"P{i+1}", use_container_width=True)
                            
                            if len(results['page_images']) > 5:
                                st.caption(f"... and {len(results['page_images']) - 5} more pages")
                    else:
                        st.info("No page images extracted.")
                
                with img_tab2:
                    st.write("**Table Images:**")
                    if results['table_images']:
                        # Show all tables in a grid layout
                        if len(results['table_images']) == 1:
                            img_path = results['table_images'][0]
                            if os.path.exists(img_path):
                                st.image(img_path, caption="Table 1", use_container_width=True)
                        else:
                            # Show tables in a 2-column grid for better viewing
                            for i in range(0, len(results['table_images']), 2):
                                cols = st.columns(2)
                                for j, col in enumerate(cols):
                                    if i + j < len(results['table_images']):
                                        img_path = results['table_images'][i + j]
                                        if os.path.exists(img_path):
                                            with col:
                                                st.image(img_path, caption=f"Table {i + j + 1}", use_container_width=True)
                        
                        st.info(f"📊 Total tables extracted: {len(results['table_images'])}")
                    else:
                        st.info("No table images extracted.")
                
                with img_tab3:
                    st.write("**Picture/Figure Images:**")
                    if results['picture_images']:
                        # Show all pictures in a grid layout
                        if len(results['picture_images']) == 1:
                            img_path = results['picture_images'][0]
                            if os.path.exists(img_path):
                                st.image(img_path, caption="Picture 1", use_container_width=True)
                        else:
                            # Show pictures in a 2-column grid for better viewing
                            for i in range(0, len(results['picture_images']), 2):
                                cols = st.columns(2)
                                for j, col in enumerate(cols):
                                    if i + j < len(results['picture_images']):
                                        img_path = results['picture_images'][i + j]
                                        if os.path.exists(img_path):
                                            with col:
                                                st.image(img_path, caption=f"Picture {i + j + 1}", use_container_width=True)
                        
                        st.info(f"🖼️ Total pictures extracted: {len(results['picture_images'])}")
                    else:
                        st.info("No picture images extracted.")
                
                # Summary section at the bottom
                st.markdown("---")
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                with col_sum1:
                    st.metric("📄 Pages", len(results.get('page_images', [])))
                with col_sum2:
                    st.metric("📊 Tables", len(results.get('table_images', [])))
                with col_sum3:
                    st.metric("🖼️ Pictures", len(results.get('picture_images', [])))
            
            with view_tab3:
                st.subheader("Generated Files")
                
                # Markdown files
                if results['markdown_files']:
                    st.write("**Markdown Files:**")
                    for md_file in results['markdown_files']:
                        if os.path.exists(md_file):
                            st.write(f"📝 `{os.path.basename(md_file)}`")
                
                # HTML files
                if results['html_files']:
                    st.write("**HTML Files:**")
                    for html_file in results['html_files']:
                        if os.path.exists(html_file):
                            st.write(f"🌐 `{os.path.basename(html_file)}`")
                
                # JSON files
                if results.get('json_files'):
                    st.write("**JSON Files:**")
                    json_files = results['json_files']
                    
                    # Create expandable sections for each JSON file type
                    if json_files.get('text_tables') and os.path.exists(json_files['text_tables']):
                        with st.expander("📊 Text & Tables JSON", expanded=False):
                            st.write(f"📄 `{os.path.basename(json_files['text_tables'])}`")
                            st.caption("Contains: Document text and tables (no images, references, or bibliography)")
                            try:
                                with open(json_files['text_tables'], 'r', encoding='utf-8') as f:
                                    json_data = json.load(f)
                                    st.metric("Sections", json_data.get('statistics', {}).get('total_sections', 0))
                                    st.metric("Tables", json_data.get('statistics', {}).get('total_tables', 0))
                            except Exception as e:
                                st.error(f"Error reading JSON: {e}")
                    
                    if json_files.get('full_content') and os.path.exists(json_files['full_content']):
                        with st.expander("🖼️ Full Content JSON", expanded=False):
                            st.write(f"📄 `{os.path.basename(json_files['full_content'])}`")
                            st.caption("Contains: Complete document with images, text, tables, and references")
                            try:
                                with open(json_files['full_content'], 'r', encoding='utf-8') as f:
                                    json_data = json.load(f)
                                    stats = json_data.get('statistics', {})
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Sections", stats.get('total_sections', 0))
                                    with col2:
                                        st.metric("Tables", stats.get('total_tables', 0))
                                    with col3:
                                        st.metric("Images", stats.get('total_images', 0))
                                    with col4:
                                        st.metric("References", stats.get('total_references', 0))
                            except Exception as e:
                                st.error(f"Error reading JSON: {e}")
                    
                    if json_files.get('metadata_references') and os.path.exists(json_files['metadata_references']):
                        with st.expander("📚 Metadata & References JSON", expanded=False):
                            st.write(f"📄 `{os.path.basename(json_files['metadata_references'])}`")
                            st.caption("Contains: Document metadata and structured references")
                            try:
                                with open(json_files['metadata_references'], 'r', encoding='utf-8') as f:
                                    json_data = json.load(f)
                                    ref_stats = json_data.get('reference_statistics', {})
                                    metadata = json_data.get('metadata', {})
                                    
                                    if metadata.get('title'):
                                        st.write(f"**Title:** {metadata['title']}")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Total References", ref_stats.get('total_references', 0))
                                        st.metric("With DOI", ref_stats.get('references_with_doi', 0))
                                    with col2:
                                        st.metric("With PMID", ref_stats.get('references_with_pmid', 0))
                                        
                                    # Show reference types breakdown
                                    ref_types = ref_stats.get('reference_types', {})
                                    if ref_types:
                                        st.write("**Reference Types:**")
                                        for ref_type, count in ref_types.items():
                                            st.write(f"- {ref_type.replace('_', ' ').title()}: {count}")
                            except Exception as e:
                                st.error(f"Error reading JSON: {e}")
                
                # Download buttons (if needed)
                if results.get('text_file') and os.path.exists(results['text_file']):
                    with open(results['text_file'], 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    st.download_button(
                        label="📥 Download Text",
                        data=text_content,
                        file_name=f"{results['pdf_name']}-text.txt",
                        mime="text/plain"
                    )
            
            with view_tab4:
                st.subheader("Raw Processing Data")
                st.json(results, expanded=False)
        
        else:
            st.info("Upload and process a PDF file to view results here.")
            st.markdown("""
            **Docling Features:**
            - 🔍 Advanced text extraction
            - 🖼️ Image and figure extraction
            - 📊 Table detection and extraction
            - 📄 Multiple output formats (Markdown, HTML, Text)
            - 🎯 High-quality OCR and layout analysis
            """)
