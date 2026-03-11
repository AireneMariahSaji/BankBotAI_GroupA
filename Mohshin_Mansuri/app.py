import streamlit as st
from datetime import datetime
import random
import requests
import json
import time

# Set page config
st.set_page_config(
    page_title="BankBot AI Chatbot",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL
API_URL = "http://localhost:5000/api"
OLLAMA_API_URL = "http://localhost:11434"

# Utility function to check Ollama status
def check_ollama_status():
    """Check if Ollama is running and available."""
    try:
        response = requests.get(OLLAMA_API_URL, timeout=2)
        return response.status_code == 200
    except:
        return False

def check_ollama_models():
    """Get available Ollama models."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m.get("name", "Unknown") for m in models]
    except:
        pass
    return []

def test_ollama_response(model_name):
    """Test if Ollama can generate a response."""
    try:
        payload = {
            "model": model_name,
            "prompt": "Hello, I am a banking assistant.",
            "stream": False,
        }
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json=payload,
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
    except:
        pass
    return None

# Custom CSS for better styling
st.markdown("""
    <style>
    .header-title {
        color: #1f77b4;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .header-subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #1f77b4;
        color: white;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        margin-left: 50px;
        width: fit-content;
        max-width: 70%;
    }
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        margin-right: 50px;
        width: fit-content;
        max-width: 70%;
    }
    .timestamp {
        font-size: 0.75rem;
        color: #999;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "session_counter" not in st.session_state:
    st.session_state.session_counter = 0

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" or "register"

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

# Load chat history from database if user is logged in
def load_chat_history_from_db():
    """Load chat history from database and populate chat_sessions."""
    if st.session_state.is_logged_in and not st.session_state.history_loaded:
        try:
            history_response = requests.get(f"{API_URL}/history/{st.session_state.user_id}")
            if history_response.status_code == 200:
                history_data = history_response.json()
                # Group messages into sessions (groups of messages within reasonable time gaps)
                st.session_state.chat_sessions = []
                st.session_state.session_counter = 0
                
                if history_data['history']:
                    session_messages = []
                    prev_timestamp = None
                    
                    for msg in history_data['history']:
                        msg_timestamp = datetime.fromisoformat(msg['timestamp'])
                        
                        # Create a new session if there's a gap > 30 minutes between messages
                        if prev_timestamp and (msg_timestamp - prev_timestamp).total_seconds() > 1800:
                            if session_messages:
                                st.session_state.session_counter += 1
                                st.session_state.chat_sessions.append({
                                    "id": st.session_state.session_counter,
                                    "messages": session_messages.copy(),
                                    "created_at": session_messages[0]["timestamp"]
                                })
                            session_messages = []
                        
                        session_messages.append({
                            "role": "user",
                            "content": msg['message'],
                            "timestamp": msg_timestamp
                        })
                        session_messages.append({
                            "role": "assistant",
                            "content": msg['response'],
                            "timestamp": msg_timestamp
                        })
                        prev_timestamp = msg_timestamp
                    
                    # Add the last session
                    if session_messages:
                        st.session_state.session_counter += 1
                        st.session_state.chat_sessions.append({
                            "id": st.session_state.session_counter,
                            "messages": session_messages,
                            "created_at": session_messages[0]["timestamp"]
                        })
                
                st.session_state.history_loaded = True
        except:
            st.session_state.history_loaded = True
            pass

# Load history on page load if user is logged in
load_chat_history_from_db()

# Sidebar for authentication
with st.sidebar:
    st.markdown("### 🔐 Authentication")
    
    if not st.session_state.is_logged_in:
        # Login/Register Form
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
        
        with auth_tab1:
            st.markdown("**Login to your account**")
            login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            login_password = st.text_input("Password", key="login_password", type="password", placeholder="Enter your password")
            
            if st.button("Login", use_container_width=True, key="login_btn"):
                if login_username and login_password:
                    try:
                        response = requests.post(
                            f"{API_URL}/login",
                            json={"username": login_username, "password": login_password}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.is_logged_in = True
                            st.session_state.user_id = data['user_id']
                            st.session_state.user_name = data['username']
                            st.session_state.chat_sessions = []
                            st.session_state.messages = []
                            st.session_state.current_session_id = None
                            st.session_state.history_loaded = False  # Reset to trigger loading
                            
                            st.success(f"Welcome back, {data['username']}! 👋")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
                else:
                    st.warning("Please enter both username and password")
        
        with auth_tab2:
            st.markdown("**Create a new account**")
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            reg_password = st.text_input("Password", key="reg_password", type="password", placeholder="Create a password")
            reg_password_confirm = st.text_input("Confirm Password", key="reg_password_confirm", type="password", placeholder="Confirm your password")
            
            if st.button("Register", use_container_width=True, key="register_btn"):
                if reg_username and reg_password and reg_password_confirm:
                    if reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    else:
                        try:
                            response = requests.post(
                                f"{API_URL}/register",
                                json={"username": reg_username, "password": reg_password}
                            )
                            
                            if response.status_code == 201:
                                st.success("Account created! Please login to continue.")
                            else:
                                data = response.json()
                                st.error(data.get('error', 'Registration failed'))
                        except Exception as e:
                            st.error(f"Connection error: {str(e)}")
                else:
                    st.warning("Please fill in all fields")
    
    else:
        # User logged in
        st.markdown(f"**👤 {st.session_state.user_name}**")
        st.markdown(f"ID: `{st.session_state.user_id}`")
        
        # New Chat button
        if st.button("➕ New Chat", use_container_width=True, key="new_chat_btn"):
            # Start new empty session without saving
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.rerun()
        
        st.markdown("---")
        
        # Chat History
        if st.session_state.chat_sessions or st.session_state.messages:
            st.markdown("### 📋 Chat History")
            
            # Show current chat if it has messages
            if st.session_state.messages and st.session_state.current_session_id is None:
                first_user_msg = next((m for m in st.session_state.messages if m["role"] == "user"), None)
                if first_user_msg:
                    preview = first_user_msg["content"][:35] + "..." if len(first_user_msg["content"]) > 35 else first_user_msg["content"]
                    st.markdown(f"**📌 Current:** 💬 {preview}")
            
            # Show past sessions
            if st.session_state.chat_sessions:
                for session in reversed(st.session_state.chat_sessions):  # Show newest first
                    if session["messages"]:
                        # Get first user message as preview
                        first_user_msg = next((m for m in session["messages"] if m["role"] == "user"), None)
                        if first_user_msg:
                            preview = first_user_msg["content"][:28] + "..." if len(first_user_msg["content"]) > 28 else first_user_msg["content"]
                            session_time = session["created_at"].strftime("%H:%M")
                            
                            col1, col2 = st.columns([0.85, 0.15])
                            with col1:
                                if st.button(
                                    f"💬 {preview}\n{session_time}",
                                    use_container_width=True,
                                    key=f"session_{session['id']}"
                                ):
                                    st.session_state.messages = session["messages"].copy()
                                    st.session_state.current_session_id = None
                                    st.rerun()
                            
                            with col2:
                                if st.button(
                                    "🗑️",
                                    key=f"delete_{session['id']}",
                                    help="Delete this chat"
                                ):
                                    st.session_state.chat_sessions = [s for s in st.session_state.chat_sessions if s["id"] != session["id"]]
                                    st.rerun()
        
        # Ollama Status Panel
        st.markdown("---")
        st.markdown("### 🤖 Ollama Status")
        with st.expander("Test Ollama Connection & Models", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Check Status", use_container_width=True, key="check_ollama"):
                    with st.status("Checking Ollama...", expanded=True) as status:
                        # Check if Ollama is running
                        st.write("🔍 Checking Ollama service...")
                        is_running = check_ollama_status()
                        
                        if is_running:
                            st.success("✓ Ollama is running!")
                            
                            # Get available models
                            st.write("📚 Fetching available models...")
                            models = check_ollama_models()
                            
                            if models:
                                st.success(f"✓ Found {len(models)} model(s):")
                                for model in models:
                                    st.info(f"• {model}")
                            else:
                                st.warning("⚠️ No models found!")
                                st.error("👉 Run in PowerShell: `ollama pull neural-chat`")
                                st.caption("or try: `ollama pull orca-mini` (fastest)")
                        else:
                            st.error("✗ Ollama is not running!")
                            st.error("👉 Start Ollama from Start Menu or run: `ollama serve`")
                        
                        status.update(label="Check complete!", state="complete")
            
            with col2:
                if st.button("Test Response", use_container_width=True, key="test_response"):
                    models = check_ollama_models()
                    if models:
                        model_name = models[0]
                        with st.status("Generating test response...", expanded=True) as status:
                            st.write(f"Using model: {model_name}")
                            st.write("Sending test prompt (this should be fast)...")
                            
                            start_time = time.time()
                            response = test_ollama_response(model_name)
                            elapsed = time.time() - start_time
                            
                            if response:
                                st.success(f"✓ Response in {elapsed:.2f}s!")
                                st.info(f"Response: {response[:150]}...")
                            else:
                                st.error("✗ Failed to generate response. Model might be offline.")
                            
                            status.update(label="Test complete!", state="complete")
                    else:
                        st.error("No models available! Pull one first.")
            
            st.markdown("---")
            st.markdown("#### ⚡ Fast Models (Recommended)")
            st.caption("**orca-mini** - Fastest (3-5s), 2.7GB")
            st.caption("**neural-chat** - Fast (5-10s), 5GB") 
            st.caption("**mistral** - Balanced (10-15s), 4GB")
            st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.is_logged_in = False
            st.session_state.user_name = None
            st.session_state.user_id = None
            st.session_state.messages = []
            st.session_state.chat_sessions = []
            st.session_state.history_loaded = False
            st.rerun()
            st.session_state.current_session_id = None
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ Quick Actions")
    
    quick_actions = {
        "Check Balance": "What is my account balance?",
        "Recent Transactions": "Show me my recent transactions",
        "Apply for Loan": "I want to apply for a loan",
        "Credit Card Info": "Tell me about your credit cards",
        "Transfer Funds": "How do I transfer money?",
        "Reset Password": "I need to reset my password",
    }
    
    for action_name, action_prompt in quick_actions.items():
        if st.button(f"📍 {action_name}", use_container_width=True, key=f"quick_{action_name}"):
            if st.session_state.is_logged_in:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": action_prompt,
                    "timestamp": datetime.now()
                })
                
                # Get response from backend with loading spinner
                with st.spinner("⏳ Getting response..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={"user_id": st.session_state.user_id, "message": action_prompt}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": data['response'],
                                "timestamp": datetime.fromisoformat(data['timestamp'])
                            })
                        else:
                            error_msg = response.json().get('error', 'Failed to get response')
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"Error: {error_msg}",
                                "timestamp": datetime.now()
                            })
                    except Exception as e:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Connection error: {str(e)}. Make sure the backend is running on http://localhost:5000",
                            "timestamp": datetime.now()
                        })
                
                # Auto-save to chat history
                if st.session_state.current_session_id is None:
                    st.session_state.session_counter += 1
                    session_id = st.session_state.session_counter
                    st.session_state.chat_sessions.append({
                        "id": session_id,
                        "messages": st.session_state.messages.copy(),
                        "created_at": datetime.now()
                    })
                    st.session_state.current_session_id = session_id
                else:
                    for session in st.session_state.chat_sessions:
                        if session["id"] == st.session_state.current_session_id:
                            session["messages"] = st.session_state.messages.copy()
                            break
                
                st.rerun()
            else:
                st.warning("Please login first")


# Main content
st.markdown('<div class="header-title">🏦 BankBot AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Your AI-Powered Banking Assistant</div>', unsafe_allow_html=True)

if not st.session_state.is_logged_in:
    st.info("👋 Please login or register in the sidebar to start chatting with BankBot!")
else:
    # Chat display
    st.markdown("### 💬 Chat History")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="user-message">➤ {message["content"]}'
                    f'<div class="timestamp">{message["timestamp"].strftime("%H:%M:%S")}</div></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="bot-message">🤖 {message["content"]}'
                    f'<div class="timestamp">{message["timestamp"].strftime("%H:%M:%S")}</div></div>',
                    unsafe_allow_html=True
                )
    
    st.markdown("---")
    
    # Input area
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        user_input = st.text_input(
            "You: ",
            placeholder="Type your banking question here...",
            label_visibility="collapsed",
            key="user_input"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Process user input
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        # Show loading spinner while getting response
        with st.spinner("⏳ BankBot is thinking..."):
            # Send to backend and get response
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"user_id": st.session_state.user_id, "message": user_input}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data['response'],
                        "timestamp": datetime.fromisoformat(data['timestamp'])
                    })
                else:
                    error_msg = response.json().get('error', 'Failed to get response')
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {error_msg}",
                        "timestamp": datetime.now()
                    })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Connection error: {str(e)}. Make sure the backend is running on http://localhost:5000",
                    "timestamp": datetime.now()
                })
        
        # Auto-save current session to chat history if current_session_id is None
        if st.session_state.current_session_id is None:
            st.session_state.session_counter += 1
            session_id = st.session_state.session_counter
            st.session_state.chat_sessions.append({
                "id": session_id,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now()
            })
            st.session_state.current_session_id = session_id
        else:
            # Update existing session
            for session in st.session_state.chat_sessions:
                if session["id"] == st.session_state.current_session_id:
                    session["messages"] = st.session_state.messages.copy()
                    break
        
        st.rerun()

# Footer with system status
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    ollama_status = "🟢 Online" if check_ollama_status() else "🔴 Offline"
    st.metric("Ollama Status", ollama_status)

with col2:
    if st.session_state.is_logged_in:
        st.metric("User", st.session_state.user_name)
    else:
        st.metric("Status", "Not logged in")

with col3:
    total_msgs = sum(len(session["messages"]) for session in st.session_state.chat_sessions) + len(st.session_state.messages)
    st.metric("Total Messages", total_msgs)

st.markdown(
    "<div style='text-align: center; color: #999; font-size: 0.9rem;'>"
    "🔒 Your conversations are secure | Powered by BankBot AI"
    "</div>",
    unsafe_allow_html=True
)
