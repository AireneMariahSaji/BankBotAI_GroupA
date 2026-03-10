import streamlit as st
import json
import random
import time
import requests
from datetime import datetime, timedelta
from typing import Optional
from banking_library import BankingLibrary

# ─── Page Config ───
st.set_page_config(
    page_title="Cassandra Bankbot AI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    /* Do NOT hide header, or you lose the sidebar toggle */
    /* header {visibility: hidden;} */

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #0f2139 100%) !important;
        border-right: 1px solid #1a3a5c !important;
        visibility: visible !important;
        display: block !important;

        /* Wider sidebar for better readability */
        min-width: 260px;
        max-width: 280px;
    }
    
    /* Optionally hide the collapse/expand button in the top bar */
    button[kind="header"] {
        display: none !important;
    }

    /* Sidebar text colors */
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: #c8ddf0 !important;
    }
    
    /* Sidebar section headings */
    section[data-testid="stSidebar"] h5 {
        color: #ffffff !important;
    }

    /* Chat Messages */
    .chat-user {
        background: #e8f4fd;
        border: 1px solid #b8daef;
        border-radius: 16px 16px 4px 16px;
        padding: 14px 20px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        color: #0a1628;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .chat-bot {
        background: #f0f4f8;
        border: 1px solid #d8e2ec;
        border-radius: 16px 16px 16px 4px;
        padding: 14px 20px;
        margin: 8px 0;
        max-width: 80%;
        color: #1a2a3a;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .chat-bot strong {
        color: #0d5c2f;
    }

    /* Login Card */
    .login-card {
        background: white;
        border-radius: 20px;
        padding: 48px 40px;
        box-shadow: 0 20px 60px rgba(10, 22, 40, 0.12);
        border: 1px solid #e2eaf2;
        max-width: 440px;
        margin: 0 auto;
    }
    .login-header {
        text-align: center;
        margin-bottom: 32px;
    }
    .login-header h1 {
        color: #0a1628;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .login-header p {
        color: #6b7c8d;
        font-size: 0.95rem;
    }

    /* Brand Logo */
    .brand-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .brand-logo-text {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0d7c44;
        letter-spacing: -0.5px;
    }
    .brand-logo-sub {
        font-size: 0.85rem;
        color: #6b7c8d;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Quick Action Button */
    .faq-btn {
        background: #f0f7f3;
        border: 1px solid #c8e6d5;
        border-radius: 12px;
        padding: 12px 16px;
        text-align: left;
        color: #0d5c2f;
        font-size: 0.88rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        width: 100%;
        display: block;
        margin-bottom: 8px;
    }
    .faq-btn:hover {
        background: #d6f0e0;
        border-color: #0d7c44;
    }

    /* Metric Card */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2eaf2;
        box-shadow: 0 2px 8px rgba(10, 22, 40, 0.04);
    }
    .metric-card h3 {
        color: #6b7c8d;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .metric-card .value {
        color: #0a1628;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-card .change-up {
        color: #0d7c44;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .metric-card .change-down {
        color: #c0392b;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, #0d7c44 0%, #0a5c32 100%);
        border-radius: 16px;
        padding: 28px 32px;
        color: white;
        margin-bottom: 24px;
    }
    .welcome-banner h2 {
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .welcome-banner p {
        color: rgba(255,255,255,0.8);
        font-size: 0.95rem;
    }

    /* Typing indicator */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 8px 16px;
        background: #f0f4f8;
        border-radius: 16px;
        margin: 8px 0;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #6b7c8d;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
        30% { transform: translateY(-6px); opacity: 1; }
    }

    /* Streamlit button overrides */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.85rem;  /* slightly smaller to prevent wrapping */
        padding: 8px 24px;
        transition: all 0.2s;
    }

    div[data-testid="stVerticalBlock"] > div:has(> .stButton) button[kind="primary"] {
        background: #0d7c44;
        border-color: #0d7c44;
    }
    div[data-testid="stVerticalBlock"] > div:has(> .stButton) button[kind="primary"]:hover {
        background: #0a5c32;
        border-color: #0a5c32;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────

def generate_sample_expenses():
    categories = ["Food & Dining", "Transport", "Shopping", "Bills & Utilities", "Entertainment", "Healthcare", "Education", "Savings"]
    expenses = []
    for i in range(20):
        cat = random.choice(categories)
        expenses.append({
            "id": i,
            "category": cat,
            "description": f"{cat} expense",
            "amount": round(random.uniform(100, 25000), 2),
            "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "type": "debit" if cat != "Savings" else "credit",
        })
    return sorted(expenses, key=lambda x: x["date"], reverse=True)


def init_session_state():
    defaults = {
        "authenticated": False,
        "username": "Demo User",
        "current_page": "login",
        "active_tab": "expenses",  # Expense dashboard is primary by default
        "chat_history": [],
        "current_chat": [],
        "current_chat_id": None,
        "expenses": generate_sample_expenses(),
        "show_signup": False,
        "users_db": {"demo": "demo123", "admin": "admin123"},
        "bank_db": BankingLibrary(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─────────────────────────────────────────────
# Ollama Integration with Llama3
# ─────────────────────────────────────────────

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "phi3"

SYSTEM_PROMPT = """You are Cassandra Bankbot AI, a specialized banking assistant for Cassandra Bank in India.

IMPORTANT: You ONLY answer banking-related queries. Banking topics include: accounts, balance, transfers, loans, credit cards, savings, investments, interest rates, fees, deposits, withdrawals, transactions, mortgages, insurance, and other banking services.

For banking questions: Provide friendly, professional support. Use INR (₹) for all amounts. Be concise and helpful. If unsure about banking matters, suggest contacting 1-800-BANKBOT.

For non-banking questions: Politely decline with a concise response. Do NOT mention the customer service number. Example: "I'm specialized in banking services and cannot assist with that query. Please feel free to ask any banking-related questions."

Always maintain a professional tone."""


def get_customer_id_from_username(username: str, bank_db: BankingLibrary) -> Optional[str]:
    customer = bank_db.get_customer_by_name(username)
    return customer["customer_id"] if customer else None


def fetch_personal_banking_info(customer_id: str, user_message: str, bank_db: BankingLibrary) -> Optional[str]:
    user_msg_lower = user_message.lower()
    customer = bank_db.get_customer(customer_id)
    if not customer:
        return None

    responses = []

    # Account balance only
    is_balance_only = any(word in user_msg_lower for word in ["balance", "current balance", "how much"])
    is_account_details = any(word in user_msg_lower for word in ["account details", "account information", "check account", "my account"])

    if (is_balance_only and not is_account_details):
        accounts = bank_db.get_customer_accounts(customer_id)
        if accounts:
            responses.append(f"**Your Account Balance:**")
            for acc in accounts:
                responses.append(f"• {acc['account_type']} Account ({acc['account_number']}): ₹{acc['balance']:,.0f}")
            return "\n".join(responses)
        else:
            return f"Hi {customer['name']}, you don't have any accounts registered with us."

    # Account details
    if is_account_details or any(word in user_msg_lower for word in ["account details", "check account"]):
        accounts = bank_db.get_customer_accounts(customer_id)
        if accounts:
            responses.append(f"**Your Account Information:**")
            for acc in accounts:
                responses.append(f"\n**{acc['account_type']} Account** ({acc['account_number']})")
                responses.append(f"• Balance: ₹{acc['balance']:,.0f}")
                responses.append(f"• Status: {acc['status']}")
                responses.append(f"• Interest Rate: {acc['interest_rate']}% APR")
            return "\n".join(responses)
        else:
            return f"Hi {customer['name']}, you don't have any accounts registered with us."

    # Loans
    if any(word in user_msg_lower for word in ["loan", "active loans", "loan status", "emi", "my loan"]):
        loans = bank_db.get_customer_loans(customer_id)
        if loans:
            responses.append(f"**Your Active Loans:**")
            for loan in loans:
                loan_details = bank_db.calculate_loan_details(loan["loan_id"])
                if loan_details:
                    responses.append(f"\n**{loan['loan_type']}** ({loan['loan_id']})")
                    responses.append(f"• Amount Borrowed: ₹{loan['amount']:,.0f}")
                    responses.append(f"• Remaining Balance: ₹{loan_details['remaining_balance']:,.0f}")
                    responses.append(f"• Monthly EMI: ₹{loan_details['monthly_emi']:,.2f}")
                    responses.append(f"• Interest Rate: {loan['interest_rate']}% APR")
                    responses.append(f"• Remaining Tenure: {loan_details['remaining_months']} months")
                    responses.append(f"• Status: {loan['status']}")
            return "\n".join(responses)
        else:
            return f"Hi {customer['name']}, you don't have any active loans."

    # Cards
    if any(word in user_msg_lower for word in ["card", "credit card", "debit card", "my cards", "card details"]):
        cards = bank_db.get_customer_cards(customer_id)
        if cards:
            responses.append(f"**Your Cards:**")
            for card in cards:
                responses.append(f"\n**{card['card_type']}** ({card['card_id']})")
                responses.append(f"• Card Number: {card['card_number']}")
                responses.append(f"• Expiry: {card['expiry']}")
                responses.append(f"• Status: {card['status']}")
                if card['card_type'] == "Debit Card":
                    responses.append(f"• Daily Limit: ₹{card.get('daily_limit', 'N/A')}")
                else:
                    cl = card.get('credit_limit', 'N/A')
                    cb = card.get('current_balance', 'N/A')
                    responses.append(f"• Credit Limit: ₹{cl:,.0f}" if isinstance(cl, (int, float)) else f"• Credit Limit: {cl}")
                    responses.append(f"• Current Balance: ₹{cb:,.0f}" if isinstance(cb, (int, float)) else f"• Current Balance: {cb}")
            return "\n".join(responses)
        else:
            return f"Hi {customer['name']}, you don't have any registered cards."

    # Transactions
    if any(word in user_msg_lower for word in ["transaction", "statement", "recent transaction", "history"]):
        accounts = bank_db.get_customer_accounts(customer_id)
        if accounts:
            responses.append(f"**Recent Transactions:**")
            for acc in accounts:
                transactions = bank_db.get_account_transactions(acc['account_number'], limit=5)
                if transactions:
                    responses.append(f"\nFrom **{acc['account_type']} Account** ({acc['account_number']}):")
                    for txn in transactions:
                        responses.append(f"• {txn['type'].capitalize()}: ₹{txn['amount']:,.0f} on {txn['date']}")
            if len(responses) > 1:
                return "\n".join(responses)
        return "You don't have any transactions to display."

    return None


def get_ollama_response(user_message: str, conversation_history: list, system_prompt: str = None) -> str:
    if system_prompt is None:
        system_prompt = SYSTEM_PROMPT
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history[-6:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg["content"][:500]
            })
        messages.append({"role": "user", "content": user_message[:500]})
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
                "temperature": 0.5,
                "top_p": 0.9,
                "top_k": 40,
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result.get("message", {}).get("content", "").strip()
            if bot_response:
                return bot_response
            else:
                return "I'm having trouble processing that. Could you rephrase your question?"
        elif response.status_code == 500:
            return "The AI model encountered an error. Try again or ask a simpler question. Make sure Ollama is running: `ollama serve`"
        else:
            return f"Connection issue (Status: {response.status_code}). Ensure Ollama is running on localhost:11434"
    
    except requests.exceptions.ConnectionError:
        return "Cannot reach Ollama on localhost:11434. Please ensure Ollama is running: `ollama serve`"
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again or ask a shorter question."
    except Exception as e:
        return f"Error: {str(e)}"


def get_hybrid_response(user_message: str, conversation_history: list, bank_db: BankingLibrary, username: str = None) -> str:
    personal_keywords = [
        "my balance", "my account", "my loan", "my card", "my cards",
        "my account type", "account balance", "current balance",
        "active loans", "loan status", "transaction history",
        "recent transaction", "account status", "account details",
        "check account", "statement"
    ]
    exclude_keywords = [
        "you offer", "do you offer", "you have", "do you have",
        "types of", "what are", "benefits of", "features of",
        "difference", "how do i", "how to apply", "to apply"
    ]
    
    user_msg_lower = user_message.lower()
    is_personal_query = any(keyword in user_msg_lower for keyword in personal_keywords)
    is_general_product_query = any(keyword in user_msg_lower for keyword in exclude_keywords)
    if is_general_product_query:
        is_personal_query = False
    
    if is_personal_query and username:
        customer_id = get_customer_id_from_username(username, bank_db)
        if customer_id:
            personal_response = fetch_personal_banking_info(customer_id, user_message, bank_db)
            if personal_response:
                return personal_response
    
    db_results = bank_db.search_relevant_data(user_message)
    formatted_db_info = bank_db.format_search_results(db_results)
    
    if formatted_db_info:
        enhanced_system_prompt = f"""{SYSTEM_PROMPT}

RELEVANT BANK DATABASE INFORMATION:
{formatted_db_info}

Use the above database information to provide accurate, specific answers. Reference this information when applicable."""
        return get_ollama_response(user_message, conversation_history, enhanced_system_prompt)
    else:
        return get_ollama_response(user_message, conversation_history, SYSTEM_PROMPT)


# ─────────────────────────────────────────────
# Login / Signup Page
# ─────────────────────────────────────────────

def render_login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="brand-logo">
            <div class="brand-logo-text">Cassandra Bankbot AI</div>
            <div class="brand-logo-sub">Intelligent Banking Assistant</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.show_signup:
            render_signup_form()
        else:
            render_login_form()


def render_login_form():
    st.markdown("### Sign In to Your Account")
    st.markdown("Enter your credentials to access your banking dashboard")
    st.markdown("")

    username = st.text_input("Username", placeholder="Enter your username", key="login_user")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

    st.markdown("")
    col_a, col_b = st.columns(2)
    with col_a:
        remember = st.checkbox("Remember me")
    with col_b:
        st.markdown("<p style='text-align:right; color:#0d7c44; font-size:0.88rem; cursor:pointer; margin-top:4px;'>Forgot password?</p>", unsafe_allow_html=True)

    st.markdown("")
    if st.button("Sign In", type="primary", use_container_width=True):
        if username and password:
            if username in st.session_state.users_db and st.session_state.users_db[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.current_page = "dashboard"
                st.session_state.active_tab = "expenses"  # open Expense Dashboard first after login
                st.rerun()
            else:
                st.error("Invalid username or password. Try **demo** / **demo123**")
        else:
            st.warning("Please enter both username and password.")

    st.markdown("")
    st.markdown("---")
    st.markdown("")
    col_c, col_d, col_e = st.columns([1, 2, 1])
    with col_d:
        if st.button("Don't have an account? Sign Up", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()

    st.markdown("")
    st.markdown("""
    <div style='text-align:center; color:#6b7c8d; font-size:0.82rem; margin-top:12px;'>
        Demo credentials: <strong>demo</strong> / <strong>demo123</strong>
    </div>
    """, unsafe_allow_html=True)


def render_signup_form():
    st.markdown("### Create Your Account")
    st.markdown("Join Cassandra Bankbot AI for smart banking assistance")
    st.markdown("")

    new_username = st.text_input("Choose a Username", placeholder="Pick a username", key="signup_user")
    new_email = st.text_input("Email Address", placeholder="you@email.com", key="signup_email")
    new_password = st.text_input("Password", type="password", placeholder="Create a strong password", key="signup_pass")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_confirm")

    st.markdown("")
    agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")

    st.markdown("")
    if st.button("Create Account", type="primary", use_container_width=True):
        if not all([new_username, new_email, new_password, confirm_password]):
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters.")
        elif not agree:
            st.warning("Please agree to the Terms of Service.")
        elif new_username in st.session_state.users_db:
            st.error("Username already exists. Please choose another.")
        else:
            st.session_state.users_db[new_username] = new_password
            st.success("Account created successfully! Please sign in.")
            time.sleep(1)
            st.session_state.show_signup = False
            st.rerun()

    st.markdown("")
    st.markdown("---")
    st.markdown("")
    col_c, col_d, col_e = st.columns([1, 2, 1])
    with col_d:
        if st.button("Already have an account? Sign In", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()


# ─────────────────────────────────────────────
# Sidebar, Chat History, Navigation
# ─────────────────────────────────────────────

def save_current_chat():
    if not st.session_state.current_chat:
        return

    title = "New Chat"
    for msg in st.session_state.current_chat:
        if msg.get("role") == "user":
            title = msg["content"][:50]
            break

    chat_entry = {
        "title": title,
        "date": datetime.now().strftime("%b %d, %I:%M %p"),
        "messages": st.session_state.current_chat.copy(),
    }

    chat_id = st.session_state.current_chat_id

    if chat_id is not None and chat_id < len(st.session_state.chat_history):
        st.session_state.chat_history[chat_id] = chat_entry
    else:
        st.session_state.chat_history.append(chat_entry)
        st.session_state.current_chat_id = len(st.session_state.chat_history) - 1


def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style='text-align:center; padding: 8px 0 16px 0;'>
            <div style='font-size:1.6rem; font-weight:800; color:#2ecc71; letter-spacing:-0.5px;'>Cassandra Bankbot AI</div>
            <div style='font-size:0.75rem; color:#5a7a94; letter-spacing:1.5px; text-transform:uppercase;'>Smart Banking</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation Buttons (updated as requested)
        st.markdown("##### Navigation")

        # AIChatbot on one line (full-width button)
        if st.button(
            "AIChatbot",
            use_container_width=True,
            type="primary" if st.session_state.active_tab == "chatbot" else "secondary",
        ):
            st.session_state.active_tab = "chatbot"
            st.rerun()

        # Expense Dashboard as two words on two lines
        if st.button(
            "Expense\nDashboard",
            use_container_width=True,
            type="primary" if st.session_state.active_tab == "expenses" else "secondary",
        ):
            st.session_state.active_tab = "expenses"
            st.rerun()

        st.markdown("---")

        # New Chat Button
        if st.button("+ New Chat", use_container_width=True):
            if st.session_state.current_chat:
                save_current_chat()
            st.session_state.current_chat = []
            st.session_state.current_chat_id = None
            st.rerun()

        st.markdown("")

        # Chat History
        st.markdown("##### Chat History")
        if st.session_state.chat_history:
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                chat_idx = len(st.session_state.chat_history) - 1 - i
                col_h, col_d = st.columns([5, 1])
                with col_h:
                    if st.button(
                        f"{chat['title']}\n{chat['date']}",
                        key=f"hist_{chat_idx}",
                        use_container_width=True,
                    ):
                        st.session_state.current_chat = chat["messages"]
                        st.session_state.current_chat_id = chat_idx
                        st.session_state.active_tab = "chatbot"
                        st.rerun()
                with col_d:
                    if st.button("x", key=f"del_{chat_idx}"):
                        st.session_state.chat_history.pop(chat_idx)
                        if st.session_state.current_chat_id == chat_idx:
                            st.session_state.current_chat = []
                            st.session_state.current_chat_id = None
                        st.rerun()
        else:
            st.markdown("<p style='color:#5a7a94; font-size:0.85rem; text-align:center; padding:12px 0;'>No chat history yet.<br>Start a conversation!</p>", unsafe_allow_html=True)

        # Bottom section
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align:center; padding:8px 0;'>
            <div style='color:#c8ddf0; font-size:0.85rem; font-weight:500;'>Signed in as</div>
            <div style='color:#2ecc71; font-size:0.95rem; font-weight:700;'>{st.session_state.username}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            if st.session_state.current_chat:
                save_current_chat()
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.current_chat = []
            st.session_state.current_chat_id = None
            st.session_state.active_tab = "expenses"
            st.rerun()


# ─────────────────────────────────────────────
# Chatbot Page
# ─────────────────────────────────────────────

def process_user_message(message: str):
    st.session_state.current_chat.append({"role": "user", "content": message})
    response = get_hybrid_response(
        message,
        st.session_state.current_chat[:-1],
        st.session_state.bank_db,
        username=st.session_state.username
    )
    st.session_state.current_chat.append({"role": "bot", "content": response})
    save_current_chat()
    st.rerun()


def render_chatbot():
    st.markdown(f"""
    <div class="welcome-banner">
        <h2>Welcome back, {st.session_state.username}!</h2>
        <p>Ask Cassandra Bankbot AI anything about banking - accounts, cards, loans, transfers, and more.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Quick Actions** (Ask Cassandra Bankbot AI anything!)")
    faq_cols = st.columns(4)
    quick_actions = [
        "How do I open an account?",
        "What credit cards do you offer?",
        "Tell me about loans",
        "How do I transfer money?",
    ]
    for i, action in enumerate(quick_actions):
        with faq_cols[i]:
            if st.button(action, key=f"faq_{i}", use_container_width=True):
                process_user_message(action)

    faq_cols2 = st.columns(4)
    quick_actions2 = [
        "Savings account details",
        "How secure is my account?",
        "Mobile banking features",
        "Tell me about your fees",
    ]
    for i, action in enumerate(quick_actions2):
        with faq_cols2[i]:
            if st.button(action, key=f"faq2_{i}", use_container_width=True):
                process_user_message(action)

    st.markdown("---")

    chat_container = st.container()
    with chat_container:
        if not st.session_state.current_chat:
            st.markdown("""
            <div style='text-align:center; padding:80px 20px; color:#6b7c8d;'>
                <div style='font-size:3rem; margin-bottom:16px;'>🏦</div>
                <h3 style='color:#0a1628; font-weight:600;'>How can I help you today?</h3>
                <p>Ask me about accounts, cards, loans, transfers, savings, security, and more.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.current_chat:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("")
    col_input, col_send = st.columns([6, 1])
    with col_input:
        user_input = st.text_input(
            "Message",
            placeholder="Type your banking question here...",
            key="chat_input",
            label_visibility="collapsed",
        )
    with col_send:
        send_clicked = st.button("Send", type="primary", use_container_width=True)

    if send_clicked and user_input:
        process_user_message(user_input)


# ─────────────────────────────────────────────
# Expense Tracking Dashboard
# ─────────────────────────────────────────────

def render_expense_dashboard():
    st.markdown(f"""
    <div class="welcome-banner">
        <h2>Expense Dashboard</h2>
        <p>Track, analyze, and manage your spending across all categories.</p>
    </div>
    """, unsafe_allow_html=True)

    expenses = st.session_state.expenses

    total_spent = sum(e["amount"] for e in expenses if e["type"] == "debit")
    total_income = sum(e["amount"] for e in expenses if e["type"] == "credit")
    net = total_income - total_spent
    avg_transaction = total_spent / max(len([e for e in expenses if e["type"] == "debit"]), 1)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Spending</h3>
            <div class="value">₹{total_spent:,.2f}</div>
            <div class="change-down">This month</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Income / Credits</h3>
            <div class="value">₹{total_income:,.2f}</div>
            <div class="change-up">This month</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Net Balance</h3>
            <div class="value" style="color:{'#0d7c44' if net >= 0 else '#c0392b'}">₹{net:,.2f}</div>
            <div class="{'change-up' if net >= 0 else 'change-down'}">{'Surplus' if net >= 0 else 'Deficit'}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg. Transaction</h3>
            <div class="value">₹{avg_transaction:,.2f}</div>
            <div class="change-down">Per expense</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Spending by Category")
        category_totals = {}
        for e in expenses:
            if e["type"] == "debit":
                category_totals[e["category"]] = category_totals.get(e["category"], 0) + e["amount"]

        if category_totals:
            import pandas as pd
            df_cat = pd.DataFrame(list(category_totals.items()), columns=["Category", "Amount"])
            df_cat = df_cat.sort_values("Amount", ascending=True)
            st.bar_chart(df_cat.set_index("Category"), horizontal=True, color="#0d7c44")

    with chart_col2:
        st.markdown("#### Daily Spending Trend")
        import pandas as pd
        daily_totals = {}
        for e in expenses:
            if e["type"] == "debit":
                daily_totals[e["date"]] = daily_totals.get(e["date"], 0) + e["amount"]

        if daily_totals:
            df_daily = pd.DataFrame(list(daily_totals.items()), columns=["Date", "Amount"])
            df_daily = df_daily.sort_values("Date")
            st.area_chart(df_daily.set_index("Date"), color="#0d7c44")

    st.markdown("")
    st.markdown("---")

    form_col, table_col = st.columns([1, 2])

    with form_col:
        st.markdown("#### Add New Expense")
        with st.form("add_expense_form", clear_on_submit=True):
            exp_cat = st.selectbox("Category", [
                "Food & Dining", "Transport", "Shopping", "Bills & Utilities",
                "Entertainment", "Healthcare", "Education", "Savings"
            ])
            exp_desc = st.text_input("Description", placeholder="e.g., Grocery shopping")
            exp_amount = st.number_input("Amount (₹)", min_value=0.01, value=500.00, step=0.01)
            exp_type = st.radio("Type", ["Debit (Expense)", "Credit (Income)"], horizontal=True)
            exp_date = st.date_input("Date", value=datetime.now())

            submitted = st.form_submit_button("Add Transaction", type="primary", use_container_width=True)
            if submitted:
                new_expense = {
                    "id": len(st.session_state.expenses),
                    "category": exp_cat,
                    "description": exp_desc if exp_desc else f"{exp_cat} expense",
                    "amount": exp_amount,
                    "date": exp_date.strftime("%Y-%m-%d"),
                    "type": "credit" if "Credit" in exp_type else "debit",
                }
                st.session_state.expenses.insert(0, new_expense)
                st.success("Transaction added successfully!")
                st.rerun()

    with table_col:
        st.markdown("#### Recent Transactions")
        import pandas as pd

        display_expenses = []
        for e in expenses[:15]:
            display_expenses.append({
                "Date": e["date"],
                "Category": e["category"],
                "Description": e["description"],
                "Amount": f"{'+ ' if e['type'] == 'credit' else '- '}₹{e['amount']:,.2f}",
                "Type": "Income" if e["type"] == "credit" else "Expense",
            })

        if display_expenses:
            df = pd.DataFrame(display_expenses)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date", width="small"),
                    "Category": st.column_config.TextColumn("Category", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="medium"),
                    "Amount": st.column_config.TextColumn("Amount", width="small"),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                }
            )
        else:
            st.info("No transactions yet. Add your first expense!")


# ─────────────────────────────────────────────
# Main App Router
# ─────────────────────────────────────────────

def main():
    init_session_state()

    # If not logged in, show login / signup
    if not st.session_state.authenticated:
        render_login_page()
        return

    # Logged in: show sidebar + content
    render_sidebar()
    
    if st.session_state.active_tab == "chatbot":
        render_chatbot()
    else:
        render_expense_dashboard()


if __name__ == "__main__":
    main()
