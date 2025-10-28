"""
Dallas Student Navigator - Streamlit Chatbot Interface
An AI-powered assistant for international students in Dallas
"""

import streamlit as st
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_module import get_web_search_agent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Dallas Student Navigator",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def format_message(message):
    """Format message with markdown support"""
    return message

@st.cache_resource
def get_agent():
    """Get the web search agent instance"""
    return get_web_search_agent()

def get_response(prompt, conversation_history):
    """Get response from web search agent"""
    try:
        agent = get_agent()
        response = agent.search_and_respond(prompt, conversation_history)
        return response
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
    
    st.info("🌐 Powered by Real-Time Web Search")
    st.caption("Queries are validated for relevance and searched on the web")
    
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
        with st.spinner("🔍 Searching the web..."):
            response = get_response(prompt, st.session_state.messages)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Powered by LangChain & DuckDuckGo Search | Built for International Students in Dallas</p>
    <p>© 2024 Dallas Student Navigator</p>
</div>
""", unsafe_allow_html=True)

