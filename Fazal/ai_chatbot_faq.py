import streamlit as st
import ollama
from datetime import datetime
import json

with open("bank_knowledge.json", "r") as f:
    BANK_KNOWLEDGE = json.load(f)

def is_bank_query(user_text):

    text = user_text.lower().strip()

    greetings = [
        "hi", "hello", "hey", "good morning",
        "good afternoon", "good evening", "greetings"
    ]

    # allow greetings
    for g in greetings:
        if text == g or text.startswith(g):
            return True

    # allow banking keywords
    for category in BANK_KNOWLEDGE.values():
        for keyword in category:
            if keyword in text:
                return True

    return False

def query_ollama(messages, model="mistral:7b-instruct"):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    msgs.extend(messages)

    res = ollama.chat(
        model=model,
        messages=msgs,
        options={
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 80
        }

    )

    return res["message"]["content"].strip()



SYSTEM_PROMPT = """
You are NovaSecure Bank Assistant.

You answer only NovaSecure Bank related banking questions.

Allowed topics:
accounts, cards, loans, payments, transfers, KYC, security, mobile banking, fees, interest, policies, support.

If the user greets you, respond:
Hello. How can I assist you with NovaSecure Bank today?

If the question is unrelated to NovaSecure Bank banking services respond exactly with:
I can assist only with NovaSecure Bank related banking queries.

Responses must be clear and short, maximum two sentences.
"""
# ────────────────────────────────────────────────
#                   PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="BankBotFAQ",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🏦"
)

# ────────────────────────────────────────────────
#               SESSION STATE INIT
# ────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = []
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'current_messages' not in st.session_state:
    st.session_state.current_messages = []
if 'current_title' not in st.session_state:
    st.session_state.current_title = None

# ────────────────────────────────────────────────
#               LOGIN PAGE STYLING
# ────────────────────────────────────────────────
login_css = """
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .top-bar {
        font-size: 48px;
        text-align: center;
        margin: 40px 0 60px 0;
        color:white;
    }
    .top-bar-icon {
        margin-right: 10px;
    }

    .form-container {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 40px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        max-width: 420px;
        margin: 0 auto;
    }

    .form-title {
        font-size: 1.6em;
        font-weight: 700;
        color: #111;
        margin-bottom: 24px;
        text-align: left;
    }

    .stTextInput > div > div > input {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 12px 14px;
        font-size: 16px;
    }

    .stTextInput label {
        color:white;
        font-weight: 600;
        margin-bottom: 6px;
        display: block;
        font-size: 15px;
    }

    .forgot-password {
        text-align: right;
        color: #2563eb;
        font-size: 14px;
        margin: 4px 0 16px 0;
        display: block;
    }
    .forgot-password:hover {
        text-decoration: underline;
    }

    .login-button {
        background-color: #111827 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 12px !important;
    }
    .login-button:hover {
        background-color: #1f2937 !important;
    }
</style>
"""

# ────────────────────────────────────────────────
#            CHAT DASHBOARD STYLING
# ────────────────────────────────────────────────
chat_css = """
<style>
    .stApp { background-color: #0f1419; }
    section[data-testid="stSidebar"] {
        background-color: #1a1f26;
        border-right: 1px solid #2d3748;
    }

    .chat-header {
        text-align: center;
        padding: 24px 0 16px;
        background: linear-gradient(135deg, #1e40af, #0369a1);
        color: white;
        border-radius: 12px 12px 0 0;
        margin-bottom: 12px;
    }

    .chat-container {
        min-height: 60vh;
        max-height: 70vh;
        overflow-y: auto;
        padding: 20px;
        background: #1a1f26;
        border-radius: 12px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    }

    .stButton > button {
        border-radius: 8px;
        background-color: #1e40af;
        color: white;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #1e3a8a;
        box-shadow: 0 4px 12px rgba(30,64,175,0.35);
    }

    .history-item {
        background: #2d3748;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        color: #e2e8f0;
    }
    .history-item:hover {
        background: #374151;
    }
</style>
"""

# ────────────────────────────────────────────────
#                   LOGIN SCREEN
# ────────────────────────────────────────────────


def show_login_page():
    st.markdown(login_css, unsafe_allow_html=True)

    st.markdown("""
    <div class="top-bar">
        <span class="top-bar-icon">🏦</span> NovaSecure Bank
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        # st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown(
            '<h3 class="form-title">Login to Your Account</h3>', unsafe_allow_html=True)

        username = st.text_input(
            "Username", placeholder="Enter your username", key="login_username")
        password = st.text_input(
            "Password", placeholder="Enter your password", type="password", key="login_password")

        st.markdown(
            '<a href="#" class="forgot-password">Forgot Password?</a>', unsafe_allow_html=True)

        if st.button("Login", key="login_btn", use_container_width=True, type="primary"):
            # Very simple / fake authentication — replace with real check if needed
            if username.strip() and password.strip():
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Please enter both username and password.")

        st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────
#                CHAT DASHBOARD
# ────────────────────────────────────────────────
def show_chat_dashboard():
    st.markdown(chat_css, unsafe_allow_html=True)

    most_asked = [
        "FAQs on Accounts", "FAQs on Loans", "FAQs on Cards", "FAQs on Security",
        "FAQs on Payments", "FAQs on Transfers", "FAQs on Mobile App", "FAQs on Support"
    ]

    def create_new_chat():
        st.session_state.current_chat_id = None
        st.session_state.current_messages = []
        st.session_state.current_title = None

    def save_chat_to_history(title: str):
        if st.session_state.current_messages and title:
            chat = {
                "id": datetime.now().timestamp(),
                "title": title,
                "time": datetime.now().strftime("%b %d, %H:%M"),
                "messages": st.session_state.current_messages.copy()
            }
            st.session_state.chat_sessions.insert(0, chat)
            st.session_state.current_chat_id = chat["id"]

    def load_chat(chat_id):
        for chat in st.session_state.chat_sessions:
            if chat["id"] == chat_id:
                st.session_state.current_chat_id = chat_id
                st.session_state.current_messages = chat["messages"].copy()
                st.session_state.current_title = chat["title"]
                break

    # ─── Header ───
    st.markdown(
        '<div class="chat-header"><h1>💬 Chat Dashboard</h1>'
        '<p style="opacity:0.9">Ask anything about accounts, cards, loans & more</p></div>',
        unsafe_allow_html=True
    )

    # ─── Messages ───
    with st.container():
        if st.session_state.current_messages:
            for msg in st.session_state.current_messages:
                with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
                    st.markdown(msg["content"])
        else:
            st.markdown("""
            <div style="text-align:center; padding:100px 20px; color:#777">
                <h3>No conversation selected</h3>
                <p>Start a new chat or choose from history / popular questions</p>
            </div>
            """, unsafe_allow_html=True)

    # ─── Input ───
    if prompt := st.chat_input("Type your message here..."):
        if prompt.strip():

        # check if query is bank related
            if not is_bank_query(prompt):

                st.session_state.current_messages.append(
                {"role": "assistant", "content": "Only I can help with NovaSecure Bank related queries."}
                )

                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown("Only I can help with NovaSecure Bank related queries.")

                st.rerun()

        # show user message
        st.session_state.current_messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # prepare messages for ollama
        ollama_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.current_messages[:-1]
        ]

        ollama_messages.append({
            "role": "user",
            "content": f"Answer briefly in 2 sentences: {prompt}"
        })

        # stream assistant reply
        full_reply = ""

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()

            stream = ollama.chat(
                model="mistral:7b-instruct",
                messages=ollama_messages,
                stream=True,
                options={
                    "temperature": 0.1,
                    "num_predict": 200
                }
            )

            for chunk in stream:
                token = chunk["message"]["content"]
                full_reply += token
                placeholder.markdown(full_reply)

        # save assistant response
        st.session_state.current_messages.append(
            {"role": "assistant", "content": full_reply}
        )

        # update history
        if not st.session_state.current_title:
            title = prompt[:45] + "..." if len(prompt) > 45 else prompt
            st.session_state.current_title = title
            save_chat_to_history(title)

        else:
            for chat in st.session_state.chat_sessions:
                if chat["id"] == st.session_state.current_chat_id:
                    chat["messages"] = st.session_state.current_messages.copy()
                    break

        st.rerun()
    # ─── SIDEBAR ───
    with st.sidebar:
        st.title("🏦 BankBot")

        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
        with c2:
            if st.button("✨ New Chat", type="primary", use_container_width=True):
                create_new_chat()
                st.rerun()

        st.divider()

        st.subheader("📜 Chat History")
        if st.session_state.chat_sessions:
            for i, chat in enumerate(st.session_state.chat_sessions):
                colA, colB = st.columns([5.5, 1])
                with colA:
                    label = f"{chat['title'][:28]}{'...' if len(chat['title'])>28 else ''},\n{chat['time']}"
                    if st.button(label, key=f"hist_{i}", use_container_width=True, help="Load conversation"):
                        load_chat(chat["id"])
                        st.rerun()
                with colB:
                    if st.button("🗑", key=f"del_{i}", help="Delete"):
                        st.session_state.chat_sessions.pop(i)
                        if st.session_state.current_chat_id == chat["id"]:
                            create_new_chat()
                        st.rerun()
        else:
            st.caption("No chats yet")

        st.divider()
        
        st.subheader("🔥 Popular Questions")
        for q in most_asked:
            if st.button(q, key=f"faq_{q}", use_container_width=True):
                create_new_chat()
                st.session_state.current_title = q

                # force single concise FAQ answer
                faq_prompt = f"Provide a short 2 sentence FAQ answer about {q.replace('FAQs on ','').lower()} at NovaSecure Bank."

                ai_messages = [{"role": "user", "content": faq_prompt}]
                ai_answer = query_ollama(ai_messages, model="mistral:7b-instruct")

                st.session_state.current_messages = [{"role": "user", "content": q},{"role": "assistant", "content": ai_answer}]

                save_chat_to_history(q)
                st.rerun()

# ────────────────────────────────────────────────
#                   MAIN LOGIC
# ────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login_page()
else:
    show_chat_dashboard()