import ollama
import streamlit as st
import json

with open("bank_data.json", "r") as file:
    bank_data = json.load(file)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SecureBank AI",
    page_icon="🏦",
    layout="wide"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}

/* Main Title */
h1 {
    color: #0f172a !important;
    font-weight: 800;
}

/* Input Labels */
/* Username & Password Labels */
label {
    color: #0f172a !important;   /* Dark Navy */
    font-weight: 600 !important;
    font-size: 15px !important;
}
*

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}


/* SIMPLE FIX – MAKE CHAT VISIBLE */

/* All chat bubbles */
div[data-testid="stChatMessage"] {
    background-color: #e5e7eb !important;   /* light grey */
    color: #111827 !important;              /* dark text */
    border-radius: 14px !important;
    padding: 12px !important;
}

/* Force text color inside */
div[data-testid="stChatMessage"] * {
    color: #111827 !important;
}
/* Buttons Default */
.stButton > button {
    background-color: #0f172a !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    border: none !important;
}

/* Button Hover */
.stButton > button:hover {
    background-color: #1d4ed8 !important;   /* Blue on hover */
    color: white !important;
    border: none !important;
}

/* Button Active (when clicked) */
.stButton > button:active {
    background-color: #2563eb !important;
    color: white !important;
}
            /* Spinner text color */
div[data-testid="stSpinner"] {
    color: #0f172a !important;   /* Dark navy */
    font-weight: 600 !important;
}


</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "messages" not in st.session_state:
    st.session_state.messages = {}


if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- SIGNUP ----------------
def signup():
    st.title("🏦 SecureBank AI - Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if username in st.session_state.users:
            st.warning("User already exists")
        else:
            st.session_state.users[username] = password
            st.success("Account created successfully")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- LOGIN ----------------
def login():
    st.title("🏦 SecureBank AI - Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.rerun()
        else:
            st.error("Invalid credentials")
    if username not in st.session_state.messages:
        st.session_state.messages[username] = []


    if st.button("Create New Account"):
        st.session_state.page = "signup"
        st.rerun()

# ---------------- MAIN APP ----------------
def main_app():

    st.title("🏦 SecureBank AI")
    st.markdown(f"""
    <h3 style='color:#0f172a; font-weight:700;'>
    Welcome, {st.session_state.current_user} 👋
    </h3>
    """, unsafe_allow_html=True)


    # -------- Sidebar Dashboard --------
    with st.sidebar:
        st.header("📊 Account Overview")

        st.metric("Available Balance", "₹25,000")
        st.metric("Active Cards", "2")
        st.metric("Next EMI", "₹4,500")

        st.markdown("---")

        service = st.selectbox(
            "Select Service",
            [
                "General Query",
                "Account Balance",
                "Loan Information",
                "Credit Card",
                "Transaction History",
                "EMI Details"
            ]
        )

        if st.button("Clear Chat"):
            st.session_state.messages[st.session_state.current_user] = []


        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.messages = []
            st.session_state.page = "login"
            st.rerun()
        st.markdown("---")
        st.subheader("🕘 Previous Conversations")

        current_user = st.session_state.current_user

        if current_user in st.session_state.messages and st.session_state.messages[current_user]:

            user_msgs = [
                m["content"]
                for m in st.session_state.messages[current_user]
                if m["role"] == "user"
            ]

            st.markdown(f"**Total Queries:** {len(user_msgs)}")

            for i, msg in enumerate(user_msgs):
                with st.expander(f"💬 Query {i+1}"):
                    st.write(msg)

        else:
            st.write("No previous chats yet.")

       

    st.markdown("---")

    # -------- Chat Messages --------
    user_msgs = st.session_state.messages[st.session_state.current_user]

    for msg in user_msgs:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -------- Chat Input (Auto Bottom) --------

    prompt = st.chat_input("Ask your banking question...")

    if prompt:
        st.session_state.messages[st.session_state.current_user].append(
            {"role": "user", "content": prompt}
        )

        user_input = prompt.lower()

        # --- Check JSON first ---
        if "home loan" in user_input:
            reply = f"""
    Home Loan Details:
    Interest Rate: {bank_data['loan_information']['home_loan']['interest_rate']}
    Maximum Tenure: {bank_data['loan_information']['home_loan']['max_tenure']}
    Processing Fee: {bank_data['loan_information']['home_loan']['processing_fee']}
    """

        elif "personal loan" in user_input:
            reply = f"""
    Personal Loan Details:
    Interest Rate: {bank_data['loan_information']['personal_loan']['interest_rate']}
    Maximum Tenure: {bank_data['loan_information']['personal_loan']['max_tenure']}
    Processing Fee: {bank_data['loan_information']['personal_loan']['processing_fee']}
    """

        elif "gold card" in user_input:
            reply = f"""
    Gold Credit Card:
    Annual Fee: {bank_data['credit_card']['gold_card']['annual_fee']}
    Limit: {bank_data['credit_card']['gold_card']['limit']}
    """

        else:
            with st.spinner("SecureBank AI is thinking..."):
                response = ollama.chat(
                    model="llama3",
                    messages=[
                        {"role": "system","content": """You are SecureBank AI, a professional banking assistant. Give short, clear answers. Only answer banking questions."""}
                    ] + st.session_state.messages[st.session_state.current_user]
                )
            reply = response["message"]["content"]

        # Append assistant reply
        st.session_state.messages[st.session_state.current_user].append(
            {"role": "assistant", "content": reply}
        )

        st.rerun()

# ---------------- ROUTING ----------------
if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        signup()
    else:
        login()
else:
    main_app()


