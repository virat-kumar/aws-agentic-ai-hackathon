"""
Dallas Student Navigator - Streamlit Chatbot Interface
An AI-powered assistant for international students in Dallas
"""

import streamlit as st
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Dallas Student Navigator",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize AWS Bedrock client
@st.cache_resource
def init_bedrock_client():
    """Initialize AWS Bedrock client"""
    try:
        client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        return client
    except Exception as e:
        st.error(f"Error initializing Bedrock client: {e}")
        return None

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "bedrock_client" not in st.session_state:
    st.session_state.bedrock_client = init_bedrock_client()

def format_message(message):
    """Format message with markdown support"""
    return message

def invoke_bedrock(prompt, conversation_history):
    """Invoke AWS Bedrock with the prompt"""
    if not st.session_state.bedrock_client:
        return "Error: Bedrock client not initialized. Please check your AWS credentials."
    
    try:
        # Build the conversation context
        system_prompt = """You are a helpful AI assistant for international students in Dallas, Texas. 
        You provide guidance on:
        - Housing options and neighborhoods
        - Grocery stores and shopping
        - Transportation (public transit, rideshare)
        - Legal requirements (visa, work permits)
        - Cultural tips and integration
        
        Be friendly, empathetic, and provide practical, actionable advice."""
        
        # Prepare the full conversation for the model
        conversation_text = f"{system_prompt}\n\n"
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Keep last 10 exchanges
            if msg["role"] == "user":
                conversation_text += f"\nUser: {msg['content']}\n"
            elif msg["role"] == "assistant":
                conversation_text += f"\nAssistant: {msg['content']}\n"
        
        conversation_text += f"\nUser: {prompt}\n\nAssistant:"
        
        # For now, return a placeholder response
        # In production, you would invoke the actual Bedrock model
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-v2')
        
        response_text = "I'm an AI assistant to help international students in Dallas. "
        response_text += "I can help you with housing, groceries, transportation, legal matters, and cultural tips. "
        response_text += "How can I assist you today?"
        
        return response_text
        
    except Exception as e:
        return f"Error: {str(e)}"

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 2rem;
    }
    .stButton>button:hover {
        background-color: #155a8b;
    }
</style>
""", unsafe_allow_html=True)

# Main UI
st.markdown('<div class="main-header">🌟 Dallas Student Navigator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your AI Assistant for Life in Dallas</div>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("📚 About")
    st.markdown("""
    This AI assistant helps international students with:
    - 🏠 Housing assistance
    - 🛒 Grocery shopping
    - 🚌 Transportation
    - ⚖️ Legal requirements
    - 🌍 Cultural integration
    """)
    
    st.header("🚀 Quick Links")
    st.button("Housing", use_container_width=True)
    st.button("Groceries", use_container_width=True)
    st.button("Transportation", use_container_width=True)
    st.button("Legal Info", use_container_width=True)
    st.button("Cultural Tips", use_container_width=True)
    
    st.divider()
    
    st.header("⚙️ Settings")
    model_choice = st.selectbox(
        "Choose Model",
        ["Claude 3 Sonnet", "Claude 3 Opus", "Llama 2"]
    )
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    if st.button("Clear Chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about living in Dallas..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = invoke_bedrock(prompt, st.session_state.messages)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Powered by AWS Bedrock | Built for International Students in Dallas</p>
    <p>© 2024 Dallas Student Navigator</p>
</div>
""", unsafe_allow_html=True)

