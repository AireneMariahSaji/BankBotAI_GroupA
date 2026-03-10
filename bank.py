import streamlit as st
import json
import os
from datetime import datetime
# --- Page Config ---
st.set_page_config(page_title="BankBot AI", page_icon="🏦", layout="wide")
# --- Load FAQ Data ---
@st.cache_data
def load_faqs():
    faq_dir = os.path.join(os.path.dirname(__file__), "faqs")
    faqs = {}
    for filename in os.listdir(faq_dir):
        if filename.endswith(".json"):
            with open(os.path.join(faq_dir, filename), "r") as f:
                data = json.load(f)
                for entry in data:
                    for kw in entry["keywords"]:
                        faqs[kw] = entry
    return faqs
FAQS = load_faqs()
FRAUD_KEYWORDS = [
    "otp", "password", "pin", "bank call", "suspicious link", "lottery",
    "kyc update", "verification link", "cvv", "share otp", "won prize",
    "click this link", "urgent verification", "account blocked", "update kyc",
    "confirm identity", "social security", "ssn", "phishing", "fake",
]
# --- Session State ---
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
def new_chat():
    chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.conversations[chat_id] = {
        "title": "New Chat",
        "messages": [
            {"role": "assistant", "content": "## 👋 Welcome to BankBot AI!\n\nI'm your secure banking assistant. How can I help you today?\n\n- 💰 Check balance\n- 📜 Recent transactions\n- 🔒 Report fraud\n- 💸 Send money\n- 📊 Spending analysis\n- ❓ Help", "timestamp": datetime.now().strftime("%H:%M")}
        ],
    }
    st.session_state.active_chat = chat_id
def get_bot_response(user_input: str) -> dict:
    lower = user_input.lower()
    # Check fraud keywords first
    for kw in FRAUD_KEYWORDS:
        if kw in lower:
            # Look for specific fraud FAQ
            if kw in FAQS:
                return {"text": FAQS[kw]["response"], "is_warning": True}
            return {
                "text": "## ⚠️ Security Warning\n\nYour message contains keywords that suggest a potential **fraud attempt**. Please be cautious:\n\n- **Never share** personal banking details\n- **Verify** through official channels\n- **Report** suspicious activity immediately\n\n🛡️ Your safety is our priority.",
                "is_warning": True,
            }
    # Check FAQ keywords
    for kw, faq in FAQS.items():
        if kw in lower:
            return {"text": faq["response"], "is_warning": faq.get("is_warning", False)}
    # Default
    return {
        "text": "I'd be happy to help! Try asking about:\n\n- 💰 *Balance*\n- 📜 *Transactions*\n- 💸 *Transfers*\n- 📊 *Spending analysis*\n- 🔒 *Report fraud*\n- 💳 *Card services*\n- 🏦 *Loans*",
        "is_warning": False,
    }
def download_chat(chat_id: str) -> str:
    chat = st.session_state.conversations[chat_id]
    lines = [f"BankBot AI — {chat['title']}\n{'=' * 40}\n"]
    for msg in chat["messages"]:
        role = "You" if msg["role"] == "user" else "BankBot"
        lines.append(f"[{msg['timestamp']}] {role}:\n{msg['content']}\n")
    return "\n".join(lines)
# --- Auth Pages ---
def login_page():
    st.markdown("# 🏦 BankBot AI")
    st.markdown("### Sign in to your account")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.user = {"email": email, "name": email.split("@")[0].title()}
                    new_chat()
                    st.rerun()
                else:
                    st.error("Please enter email and password")
        if st.button("Don't have an account? Register"):
            st.session_state.page = "register"
            st.rerun()
def register_page():
    st.markdown("# 🏦 Create Account")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords don't match")
                elif name and email and password:
                    st.session_state.logged_in = True
                    st.session_state.user = {"email": email, "name": name}
                    new_chat()
                    st.rerun()
                else:
                    st.error("Please fill all fields")
        if st.button("Already have an account? Sign In"):
            st.session_state.page = "login"
            st.rerun()
# --- Main App ---
def main_app():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🏦 BankBot AI")
        st.markdown(f"👤 {st.session_state.user['name']}")
        st.divider()
        if st.button("➕ New Chat", use_container_width=True):
            new_chat()
            st.rerun()
        st.markdown("#### 💬 Chat History")
        for chat_id, chat in reversed(list(st.session_state.conversations.items())):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📄 {chat['title'][:25]}", key=f"sel_{chat_id}", use_container_width=True):
                    st.session_state.active_chat = chat_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat_id}"):
                    del st.session_state.conversations[chat_id]
                    if st.session_state.active_chat == chat_id:
                        st.session_state.active_chat = None
                    st.rerun()
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    # Main chat area
    if not st.session_state.active_chat:
        st.markdown("## 👋 Welcome! Click **New Chat** to start.")
        return
    chat = st.session_state.conversations[st.session_state.active_chat]
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🤖 {chat['title']}")
        st.caption("🟢 Online · Secure & Encrypted 🔒")
    with col2:
        txt = download_chat(st.session_state.active_chat)
        st.download_button("📥 Download Chat", txt, file_name=f"{chat['title']}.txt", use_container_width=True)
    st.divider()
    # Messages
    for msg in chat["messages"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
                st.caption(msg["timestamp"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                if msg.get("is_warning"):
                    st.warning(msg["content"])
                else:
                    st.markdown(msg["content"])
                st.caption(msg["timestamp"])
    # Quick actions (only at start)
    if len(chat["messages"]) <= 1:
        st.markdown("#### Quick Actions")
        cols = st.columns(3)
        actions = [
            ("💰 Check Balance", "What is my account balance?"),
            ("📜 Transactions", "Show my recent transactions"),
            ("🔒 Report Fraud", "I want to report suspicious activity"),
            ("💸 Send Money", "How do I transfer money?"),
            ("📊 Spending", "Show me my spending analysis"),
            ("❓ Help", "What can you help me with?"),
        ]
        for i, (label, msg) in enumerate(actions):
            with cols[i % 3]:
                if st.button(label, key=f"qa_{i}", use_container_width=True):
                    now = datetime.now().strftime("%H:%M")
                    chat["messages"].append({"role": "user", "content": msg, "timestamp": now})
                    if chat["title"] == "New Chat":
                        chat["title"] = msg[:30]
                    resp = get_bot_response(msg)
                    chat["messages"].append({"role": "assistant", "content": resp["text"], "is_warning": resp["is_warning"], "timestamp": now})
                    st.rerun()
    # Input
    if prompt := st.chat_input("Ask BankBot anything..."):
        now = datetime.now().strftime("%H:%M")
        chat["messages"].append({"role": "user", "content": prompt, "timestamp": now})
        if chat["title"] == "New Chat":
            chat["title"] = prompt[:30]
        resp = get_bot_response(prompt)
        chat["messages"].append({"role": "assistant", "content": resp["text"], "is_warning": resp["is_warning"], "timestamp": now})
        st.rerun()
    # Security footer
    st.divider()
    st.caption("🛡️ End-to-end encrypted · Never share OTP or PIN")
# --- Router ---
if not st.session_state.logged_in:
    page = st.session_state.get("page", "login")
    if page == "register":
        register_page()
    else:
        login_page()
else:
    main_app()