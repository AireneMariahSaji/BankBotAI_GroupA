import streamlit as st
import html
import time
from datetime import datetime
from datetime import timedelta
import random
# from auth import create_user, login_user
import re
import pandas as pd
import matplotlib.pyplot as plt
import base64
import json
import ollama

st.set_page_config(page_title="BankyBot AI Chat", layout="wide", initial_sidebar_state="expanded")

# --- Knowledge Base ---
def load_knowledge_base(file_path="knowledge_base.json"):
    """Loads the knowledge base from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Knowledge base file not found at '{file_path}'. Please create it.")
        # Return a default structure to avoid crashing the app
        return {"bank_name": "BankyBot", "allowed_topics": [], "restricted_topics": [], "faqs": [], "contact_details": {}}
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from '{file_path}'. Please check its format.")
        return {"bank_name": "BankyBot", "allowed_topics": [], "restricted_topics": [], "faqs": [], "contact_details": {}}

KNOWLEDGE_BASE = load_knowledge_base()

# --- Spam Detection ---
SPAM_KEYWORDS = ["lottery", "prize", "won cash", "urgent transfer", "send money", "wire transfer", "inheritance", "bank details"]

def check_spam(text):
    text = text.lower()
    for k in SPAM_KEYWORDS:
        if k in text:
            return True
    return False

def get_ollama_response(msg: str, user_data: dict, chat_history: list, knowledge_base: dict):
    """
    Gets a response from the Ollama Llama3 model.
    Assumes Ollama is running locally and the 'llama3' model is available.
    """
    try:
        # Construct a restrictive system prompt using the knowledge base
        contact_details = knowledge_base.get('contact_details', {})
        allowed_topics = ', '.join(knowledge_base.get('allowed_topics', ['banking']))
        restricted_topics = ', '.join(knowledge_base.get('restricted_topics', ['anything not related to banking']))

        system_prompt = f"""You are BankyBot, a specialized AI banking assistant for {knowledge_base.get('bank_name', 'the bank')}. Your ONLY function is to assist with banking-related queries.
        You must strictly adhere to the following rules:
        1.  Only answer questions related to these topics: {allowed_topics}.
        2.  You MUST refuse to answer any questions about restricted topics like: {restricted_topics}. If asked about a restricted topic, you must reply with: "I am a banking assistant and cannot help with that topic."
        3.  Do not make up information. If you don't know an answer or lack the necessary information, politely state that you cannot provide it and suggest contacting customer support at {contact_details.get('customer_care', 'the bank')}.
        4.  Be professional, clear, and friendly. Your responses should be easy to understand.
        5.  For answers that involve multiple steps, details, or lists, structure your response for maximum clarity. Use paragraphs for explanations and bullet points (`*`) or numbered lists for individual items. For example, when asked for transactions, list them clearly.

        Here is the current user's information (use it to answer questions about their account):
        - Name: {user_data.get('name')}
        - Account Number: {user_data.get('account')}
        - Balance: {user_data.get('balance')}
        - Recent Transactions: {str(user_data.get('transactions', []))}

        Here is some general information about the bank you can use:
        - FAQs: {str(knowledge_base.get('faqs', []))}

        The current conversation history is:
        """

        # Format the chat history for the model
        messages = [{"role": "system", "content": system_prompt}]
        # Add recent messages from history
        for message in chat_history[-6:]: # Use last few messages for context
            messages.append({"role": message['role'], "content": message['text']})
        
        # Add the new user message
        messages.append({"role": "user", "content": msg})

        # Call Ollama Llama3
        response = ollama.chat(
            model='llama3',
            messages=messages
        )
        return response['message']['content']

    except Exception as e:
        st.warning(f"Could not connect to Ollama. Is the service running and is 'llama3' pulled? Error: {e}")
        return "I'm having trouble connecting to my AI brain right now. Please make sure the Ollama service is running locally and try again."


# --- Styling ---
st.markdown("""
<style>
    /* Global Theme */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    
    /* Header */
    .header-title {
        font-size: 28px;
        font-weight: 700;
        color: #3b82f6;
        margin-bottom: 5px;
        text-align: center;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #94a3b8;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'conversations' not in st.session_state:
    st.session_state.conversations = {}
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'users' not in st.session_state:
    # Default test user
    st.session_state.users = {
        'user': {
            'password': '123', 
            'name': 'John Doe', 
            'email': 'john@example.com', 
            'address': '123 Tech Park, Silicon Valley, CA',
            'account': '9876543210', 
            'balance': '₹12,450.00',
            'debited': '₹2,550.00',
            'credited': '₹15,000.00',
            'transactions': [
                {"Date": "2023-10-25", "Description": "Online Shopping", "Amount": "-₹120.00", "Type": "Debit"},
                {"Date": "2023-10-24", "Description": "Salary Credit", "Amount": "+₹5,000.00", "Type": "Credit"},
                {"Date": "2023-10-20", "Description": "Grocery Store", "Amount": "-₹250.00", "Type": "Debit"},
                {"Date": "2023-10-15", "Description": "Electric Bill", "Amount": "-₹150.00", "Type": "Debit"},
                {"Date": "2023-10-01", "Description": "Freelance Work", "Amount": "+₹1,200.00", "Type": "Credit"},
            ]
        }
    }
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- Auth & Dashboard Functions ---
def login_signup_ui():
    st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🏦 Welcome to <span>BankyBot</span></h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = st.session_state.users.get(username)
                if user and user['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            submit_signup = st.form_submit_button("Create Account")
            
            if submit_signup:
                if new_user in st.session_state.users:
                    st.error("Username already exists.")
                elif new_user and new_pass:
                    st.session_state.users[new_user] = {
                        'password': new_pass,
                        'name': full_name,
                        'email': email,
                        'address': 'Update your address',
                        'account': str(random.randint(1000000000, 9999999999)),
                        'balance': '₹0.00',
                        'debited': '₹0.00',
                        'credited': '₹0.00',
                        'transactions': []
                    }
                    st.success("Account created! Please log in.")
                else:
                    st.error("Please fill all required fields.")

def dashboard_ui():
    user = st.session_state.users[st.session_state.current_user]
    st.markdown(f"<h2 style='color:#3b82f6'>Welcome back, {user['name']}!</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👤 Personal Details")
        new_name = st.text_input("Full Name", user['name'])
        new_email = st.text_input("Email", user['email'])
        new_address = st.text_input("Address", user.get('address', ''))
        st.text_input("Username", st.session_state.current_user, disabled=True)
        
        if st.button("Save Profile Changes"):
            st.session_state.users[st.session_state.current_user]['name'] = new_name
            st.session_state.users[st.session_state.current_user]['email'] = new_email
            st.session_state.users[st.session_state.current_user]['address'] = new_address
            st.success("Profile updated successfully!")
        
    with col2:
        st.markdown("### 💳 Balance")
        m1, m2, m3 = st.columns(3)
        m1.metric("Balance", user['balance'])
        m2.metric("Credited", user.get('credited', '₹0.00'))
        m3.metric("Debited", user.get('debited', '₹0.00'))
        
        st.text_input("Account Number", user['account'], disabled=True)
        st.info("Your account is active and verified.")

    st.markdown("---")
    
    # Transaction Table
    st.markdown("### 📜 Recent Transactions")
    
    # Ensure we have data to show (Frontend Demo)
    tx_data = user.get('transactions', [])
    if not tx_data:
        tx_data = [
            {"Date": "2023-11-15", "Description": "Freelance Payment", "Amount": "+₹1,200.00", "Type": "Credit"},
            {"Date": "2023-11-12", "Description": "Grocery Store", "Amount": "-₹85.50", "Type": "Debit"},
            {"Date": "2023-11-10", "Description": "Netflix Subscription", "Amount": "-₹15.99", "Type": "Debit"},
            {"Date": "2023-11-05", "Description": "Gym Membership", "Amount": "-₹45.00", "Type": "Debit"}
        ]
    
    # Custom Table CSS
    st.markdown("""
    <style>
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 8px;
            overflow: hidden;
        }
        .styled-table thead tr {
            background-color: #3b82f6;
            color: #ffffff;
            text-align: left;
        }
        .styled-table th, .styled-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #334155;
        }
        .styled-table tbody tr {
            border-bottom: 1px solid #334155;
            color: #f1f5f9;
        }
        .styled-table tbody tr:nth-of-type(even) {
            background-color: #1e293b;
        }
        .btn-download {
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
            color: white !important;
            padding: 8px 16px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 12px;
            border-radius: 50px;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
            border: none;
            box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
        }
        .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6);
            color: #fff !important;
        }
    </style>
    """, unsafe_allow_html=True)

    table_html = '<table class="styled-table"><thead><tr><th>Date</th><th>Description</th><th>Amount</th><th>Type</th><th>Receipt</th></tr></thead><tbody>'

    for tx in tx_data[:3]:
        receipt_html = f"""
        <div style="border: 2px solid #3b82f6; padding: 20px; font-family: Arial, sans-serif; max-width: 400px; background-color: #f8f9fa; color: #333;">
            <h2 style="color: #3b82f6; text-align: center; margin-bottom: 5px;">BankyBot Receipt</h2>
            <p style="text-align: center; color: #666; font-size: 12px;">Official Transaction Record</p>
            <hr style="border: 0; border-top: 1px solid #ddd;">
            <p><strong>Date:</strong> {tx['Date']}</p>
            <p><strong>Description:</strong> {tx['Description']}</p>
            <p><strong>Type:</strong> {tx['Type']}</p>
            <p><strong>Amount:</strong> <span style="color: {'#16a34a' if 'Credit' in tx['Type'] else '#dc2626'}; font-weight: bold;">{tx['Amount']}</span></p>
            <hr style="border: 0; border-top: 1px solid #ddd;">
            <p style="text-align: center; font-size: 11px; color: #888;">Transaction ID: {random.randint(100000, 999999)}</p>
            <p style="text-align: center; font-size: 11px; color: #888;">Thank you for banking with BankyBot!</p>
        </div>
        """
        b64 = base64.b64encode(receipt_html.encode()).decode()
        href = f"data:text/html;base64,{b64}"
        
        table_html += "<tr>"
        table_html += f"<td>{tx['Date']}</td>"
        table_html += f"<td>{tx['Description']}</td>"
        table_html += f"<td>{tx['Amount']}</td>"
        table_html += f"<td>{tx['Type']}</td>"
        table_html += f'<td><a href="{href}" download="receipt_{tx["Date"]}.html" class="btn-download">📥 Download PDF</a></td>'
        table_html += "</tr>"
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

# --- Main Application Flow ---
if not st.session_state.logged_in:
    # Apply custom styles for the login page
    st.markdown("""
    <style>
        /* Center the main content block for the login page */
        section[data-testid="stAppViewContainer"] > .block-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            min-height: 100vh;
        }
        /* The card container for the form elements */
        section[data-testid="stAppViewContainer"] > .block-container > div:first-child {
            background-color: #1e293b;
            padding: 2rem 2.5rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            width: 100%;
            max-width: 450px;
            border: 1px solid #334155;
        }
        
        /* Title styling */
        section[data-testid="stAppViewContainer"] > .block-container > div:first-child h1 {
            text-align: center;
            color: #e2e8f0;
            font-weight: 600;
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
        }
        section[data-testid="stAppViewContainer"] > .block-container > div:first-child h1 span {
            color: #3b82f6;
        }

        /* Style Streamlit's tabs */
        div[data-baseweb="tab-list"] {
            justify-content: center;
            background-color: transparent;
            margin-bottom: 1.5rem;
        }
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            color: #94a3b8 !important;
            border-bottom: 3px solid transparent !important;
            font-weight: 600;
            padding-bottom: 10px !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #3b82f6 !important;
            border-bottom-color: #3b82f6 !important;
        }

        /* Style form submit button */
        .stButton>button {
            width: 100%;
            background-color: #3b82f6;
            color: white;
            border-radius: 8px;
            padding: 12px 0;
            font-weight: bold;
            border: none;
            margin-top: 1rem;
            transition: background-color 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            color: white;
        }
        .stButton>button:focus {
            box-shadow: 0 0 0 3px #0f172a, 0 0 0 5px #2563eb;
            outline: none;
        }

        /* Style text inputs */
        .stTextInput input {
            background-color: #0f172a;
            color: #f1f5f9;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 22px 15px !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
        }
    </style>
    """, unsafe_allow_html=True)
    login_signup_ui()
else:
    # --- Sidebar Navigation ---
    with st.sidebar:
        st.markdown("<div style='font-size: 24px; font-weight: bold; color: #3b82f6; margin-bottom: 10px;'>🏦 BankyBot</div>", unsafe_allow_html=True)
        
        # Navigation
        page = st.radio("Navigate", ["Chatbot", "Dashboard", "Transformation Graph"], index=0)
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
            
        st.markdown("---")
        
        if page == "Transformation Graph":
            st.markdown("### 📉 Graph Settings")
            st.selectbox("Graph Type", ["Bar Chart", "Pie Chart", "Linear Graph"], key="graph_type")
            st.selectbox("Time Frame", ["Weekly", "Monthly"], key="time_frame")

    if page == "Dashboard":
        dashboard_ui()
        
    elif page == "Transformation Graph":
        st.markdown(f"### 📉 Spending Analysis")
        
        graph_type = st.session_state.get("graph_type", "Bar Chart")
        time_frame = st.session_state.get("time_frame", "Weekly")

        if time_frame == "Weekly":
            data = pd.DataFrame({'Label': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 'Value': [500, 1200, 800, 200, 2500, 4000, 1500]})
        else:
            data = pd.DataFrame({'Label': ['Week 1', 'Week 2', 'Week 3', 'Week 4'], 'Value': [12000, 15000, 8000, 20000]})

        if graph_type == "Bar Chart":
            st.bar_chart(data.set_index('Label'))
        elif graph_type == "Linear Graph":
            st.line_chart(data.set_index('Label'))
        elif graph_type == "Pie Chart":
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('none')
            ax.pie(data['Value'], labels=data['Label'], autopct='%1.1f%%', startangle=90, textprops={'color':"white"})
            ax.axis('equal')
            st.pyplot(fig)
        
    elif page == "Chatbot":
        # --- Chatbot Sidebar Logic ---
        with st.sidebar:
            selected_bank = KNOWLEDGE_BASE.get("bank_name", "BankyBot")
            
            if st.button("➕ New Chat", use_container_width=True):
                conv_id = f"conv_{datetime.now().timestamp()}"
                st.session_state.conversations[conv_id] = {
                    "title": "New Chat",
                    "messages": [],
                    "bank": selected_bank,
                    "blocked": False,
                    "warnings": 0,
                }
                st.session_state.current_conversation_id = conv_id
                st.rerun()

            st.markdown("### 🕒 History")
            
            # Group conversations by date
            convs_by_date = {"Today": [], "Yesterday": [], "Previous": []}
            today_date = datetime.now().date()
            
            sorted_conv_ids = sorted(st.session_state.conversations.keys(), reverse=True)

            for conv_id in sorted_conv_ids:
                conv_ts = float(conv_id.split('_')[1])
                conv_date = datetime.fromtimestamp(conv_ts).date()
                
                if conv_date == today_date:
                    convs_by_date["Today"].append(conv_id)
                elif conv_date == today_date - timedelta(days=1):
                    convs_by_date["Yesterday"].append(conv_id)
                else:
                    convs_by_date["Previous"].append(conv_id)

            for period, conv_ids in convs_by_date.items():
                if conv_ids:
                    st.caption(period)
                    for conv_id in conv_ids:
                        conv = st.session_state.conversations[conv_id]
                        if st.button(conv['title'], key=conv_id, use_container_width=True, help=conv['title']):
                            st.session_state.current_conversation_id = conv_id
                            st.rerun()
            
            # Download section for the current chat
            if st.session_state.current_conversation_id and st.session_state.conversations[st.session_state.current_conversation_id]['messages']:
                st.markdown("---")
                st.markdown("### 📥 Download Current Chat")
                current_conv_dl = st.session_state.conversations[st.session_state.current_conversation_id]
                current_history_dl = current_conv_dl['messages']
                current_bank_dl = current_conv_dl['bank']
                
                txt_history = f"BankyBot Chat History ({current_bank_dl})\n\n" + "\n".join([f"[{m['time']}] {m['role'].upper()}: {m['text']}" for m in current_history_dl])
                st.download_button("📄 Download .txt", txt_history, file_name=f"chat_{st.session_state.current_conversation_id}.txt")
                
                doc_history = f"<html><body><h1>Chat History - {current_bank_dl}</h1>"
                for m in current_history_dl:
                    color = "blue" if m['role'] == 'user' else "black"
                    doc_history += f"<p><strong><span style='color:{color}'>{m['role'].title()}</span> [{m['time']}]:</strong> {m['text']}</p>"
                doc_history += "</body></html>"
                st.download_button("📝 Download .doc", doc_history, file_name=f"chat_{st.session_state.current_conversation_id}.doc", mime="application/msword")

        # --- Chatbot Main Logic ---
        # If no conversation is selected/exists, start one.
        if not st.session_state.current_conversation_id:
            if not st.session_state.conversations:
                # Start a new chat automatically on first load
                conv_id = f"conv_{datetime.now().timestamp()}"
                st.session_state.conversations[conv_id] = {
                    "title": "New Chat",
                    "messages": [],
                    "bank": selected_bank,
                    "blocked": False,
                    "warnings": 0,
                }
                st.session_state.current_conversation_id = conv_id
            else:
                # If conversations exist but none is selected, select the most recent one
                st.session_state.current_conversation_id = max(st.session_state.conversations.keys())
            st.rerun()

        # Get current conversation details
        current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
        current_history = current_conv['messages']
        current_bank = current_conv['bank']

        st.markdown(f"""
            <div class="header-title">BankyBot AI Chat</div>
            <div class="header-subtitle">Support for <strong>{current_bank}</strong></div>
        """, unsafe_allow_html=True)

        # Display Chat History
        for msg in current_history:
            if msg['role'] == 'user':
                with st.chat_message(msg['role']):
                    st.write(msg['text'])
                    st.caption(f"{msg['time']}")
            else:
                with st.chat_message(msg['role'], avatar="🤖"):
                    # Basic formatting for attractive UI
                    formatted_text = html.escape(msg['text']).replace('\n', '<br>')
                    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_text)
                    
                    st.markdown(f"""
                    <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                        <div style="font-weight: bold; color: #3b82f6; margin-bottom: 5px;">BankyBot</div>
                        <div style="color: #e2e8f0; font-size: 15px; line-height: 1.5;">{formatted_text}</div>
                        <div style="text-align: right; font-size: 12px; color: #64748b; margin-top: 10px;">{msg['time']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # --- Helper to process message ---
        def process_message(text):
            conv_id = st.session_state.current_conversation_id
            conv = st.session_state.conversations[conv_id]

            # 1. Add user message to the current conversation
            conv['messages'].append({
                'role': 'user',
                'text': text,
                'time': datetime.now().strftime('%H:%M')
            })
            
            # Update title if it's the first user message
            if conv['title'] == "New Chat" and text:
                conv['title'] = text[:35] + "..." if len(text) > 35 else text

            # 2. Check Spam
            if check_spam(text):
                conv['warnings'] += 1
                if conv['warnings'] >= 2:
                    conv['blocked'] = True
                    response = "🚫 SECURITY ALERT: You have been blocked for violating our safety policies regarding money transfer spam."
                else:
                    response = "⚠️ SECURITY WARNING: Please do not share sensitive financial details or discuss lottery/unverified money transfers. This is your final warning."
            else:
                # 3. Normal Response
                user_data = st.session_state.users[st.session_state.current_user]
                response = get_ollama_response(text, user_data, conv['messages'], KNOWLEDGE_BASE)
            
            # 4. Add bot response
            conv['messages'].append({
                'role': 'bot',
                'text': response,
                'time': datetime.now().strftime('%H:%M')
            })

        # --- Suggested Questions (Features) ---
        is_blocked = st.session_state.conversations[st.session_state.current_conversation_id]['blocked']

        if not is_blocked:
            st.markdown("#### ⚡ Quick Actions")
            
            quick_qs = [
                ("💰 Check my balance?", "What is my current balance?"),
                ("📜 See transactions?", "Show me my recent transactions."),
                ("💳 Block my card?", "I need to block my card immediately."),
                ("💸 Transfer money?", "How do I transfer money?"),
                ("🏦 My active loans?", "What active loans do I have?"),
                ("📈 Check credit score?", "What is my current credit score?"),
                ("📞 Contact support?", "How do I contact customer support?"),
                ("🏠 Home loan rates?", "What are the home loan interest rates?")
            ]
            
            cols = st.columns(4)
            for i, (label, prompt) in enumerate(quick_qs):
                with cols[i % 4]:
                    if st.button(label, key=f"qa_{i}", use_container_width=True):
                        process_message(prompt)
                        st.rerun()

        # Input Area (Fixed Position via st.chat_input)
        if is_blocked:
            st.error("🚫 You have been blocked due to repeated suspicious activity regarding money transfers/spam.")
        else:
            if prompt := st.chat_input("Type your banking question here..."):
                process_message(prompt)
                st.rerun()
