import sqlite3
import json
import random
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
# Use absolute path for database
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot.db")

# Ollama Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "neural-chat:latest")  # Fast model (5-10s responses). Other options: "mistral:latest" (slower), "orca-mini:latest" (fastest)
OLLAMA_TIMEOUT = 60  # 60 seconds timeout (reduced for speed)

# Banking-related keywords for query validation
BANKING_KEYWORDS = {
    # Account related
    "account", "balance", "deposit", "withdrawal", "transfer", "transaction",
    # Cards
    "credit card", "debit card", "card", "visa", "mastercard",
    # Loans
    "loan", "mortgage", "interest rate", "emi", "personal loan", "auto loan",
    # Services
    "wire transfer", "money transfer", "send money", "receive money", "payment",
    # Support
    "password", "reset", "forgot", "security", "fraud", "dispute", "customer service",
    "help", "support", "contact", "branch", "atm",
    # Transact
    "check", "statement", "history", "transaction", "record",
    # General banking
    "bank", "banking", "account opening", "account closure", "kyc", "aadhar",
    "pan", "savings", "business", "overdraft", "credit limit"
}

def is_banking_related(user_input: str) -> bool:
    """
    Check if the user query is related to banking.
    Returns True if banking-related, False otherwise.
    """
    user_input_lower = user_input.lower()
    
    # Check for banking keywords
    for keyword in BANKING_KEYWORDS:
        if keyword in user_input_lower:
            return True
    
    # Also check for common patterns
    patterns = [
        "how to", "can i", "what is", "tell me about", "explain",
        "where", "when", "who", "which", "why", "what"
    ]
    
    # If it contains a question word and no banking keyword, still try to answer
    # but if it's clearly non-banking (like sports, movies, etc.), reject it
    non_banking_keywords = [
        "movie", "sport", "game", "weather", "recipe", "cook", "travel",
        "flight", "hotel", "restaurant", "music", "song", "artist", "actor",
        "politics", "politics", "election", "vote", "covid", "vaccine",
        "love", "relationship", "dating", "marriage", "homework", "essay",
        "maths", "science", "history", "geography", "philosophy", "religion"
    ]
    
    for keyword in non_banking_keywords:
        if keyword in user_input_lower:
            return False
    
    # If query seems too generic or short, be more strict
    if len(user_input_lower.strip()) < 3:
        return False
    
    # Default: be permissive and let Ollama try to answer
    return True

def get_ollama_session():
    """Create a requests session with retry strategy for Ollama."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def generate_bot_response_ollama(user_input: str) -> str:
    """Generate a response using Ollama with banking context."""
    try:
        session = get_ollama_session()
        
        # Concise system prompt for faster inference
        system_prompt = """You are a banking assistant. Help with accounts, loans, transfers, and support. Be brief."""
        
        # Create the prompt
        user_message = f"{system_prompt}\n\nCustomer: {user_input}\nAssistant:"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": user_message,
            "stream": False,
            "temperature": 0.5,
            "num_predict": 150,
            "top_k": 30,
            "top_p": 0.8,
        }
        
        print(f"[OLLAMA] Sending request to model: {OLLAMA_MODEL}")
        response = session.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        
        print(f"[OLLAMA] Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            if generated_text and len(generated_text) > 5:  # Ensure response is meaningful
                print(f"[OLLAMA] ✓ Response generated successfully ({len(generated_text)} chars)")
                return generated_text
            else:
                print(f"[OLLAMA] ✗ Empty or too short response: '{generated_text}'")
                return None  # Return None to trigger fallback
        else:
            print(f"[OLLAMA] ✗ HTTP error {response.status_code}: {response.text}")
            return None  # Return None to trigger fallback
        
    except requests.exceptions.Timeout as e:
        print(f"[OLLAMA] ✗ Timeout after {OLLAMA_TIMEOUT}s: {str(e)}")
        return None  # Return None to trigger fallback
    except requests.exceptions.ConnectionError as e:
        print(f"[OLLAMA] ✗ Connection failed: {str(e)}")
        print(f"[OLLAMA] Is Ollama running at {OLLAMA_API_URL}?")
        return None  # Return None to trigger fallback
    except Exception as e:
        print(f"[OLLAMA] ✗ Unexpected error: {str(e)}")
        return None  # Return None to trigger fallback

# Banking AI responses dictionary (fallback)
BANKING_RESPONSES = {
    "account": [
        "I can help you check your account balance. You can view this by logging into your account or visiting our nearest branch.",
        "To open a new account with us, please visit our website or contact our customer service team.",
        "Your account details are securely stored. Would you like to update any information?"
    ],
    "balance": [
        "Your current account balance is $5,234.50. This information is updated in real-time.",
        "To check your balance, you can use our mobile app, online banking portal, or call our customer service team.",
        "Your balance updates instantly after every transaction."
    ],
    "transaction": [
        "I can help you review your recent transactions. Would you like to see transfers, deposits, or withdrawals?",
        "Your last transaction was a transfer of $500.00 to John Doe on today at 2:30 PM.",
        "To dispute a transaction, please contact our support team with the transaction details."
    ],
    "loan": [
        "We offer various loan products including personal loans, auto loans, and mortgages.",
        "Your current loan balance is $45,000.00 with a monthly payment of $850.00.",
        "To apply for a loan, please visit our website or speak with our loan officers."
    ],
    "credit card": [
        "Your credit card limit is $10,000. Current balance due: $2,150.00",
        "We offer several credit card options with competitive rates and rewards programs.",
        "To apply for a new credit card, you can fill out an application online or visit a branch."
    ],
    "transfer": [
        "To transfer funds, you can use our online banking platform, mobile app, or visit a branch.",
        "Your transfer of $1,000.00 to account XXXX5678 was successful!",
        "Transfers typically complete within 1-2 business days."
    ],
    "password": [
        "For security reasons, never share your password with anyone. To reset your password, visit our website and click 'Forgot Password'.",
        "Your account is protected with advanced encryption technology.",
        "If you suspect unauthorized access, please contact us immediately."
    ],
    "support": [
        "Our customer support team is available 24/7 to assist you.",
        "You can reach us via phone at 1-800-BANK-BOT, email, or live chat.",
        "How can I help you today?"
    ]
}

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DATABASE}")

def generate_bot_response(user_input: str) -> str:
    """Generate a response - uses Ollama by default, falls back to static responses."""
    
    # First, check if the query is banking-related
    if not is_banking_related(user_input):
        print("[FILTER] Non-banking query detected, rejecting")
        return "I appreciate your question, but I'm specifically designed to help with banking-related queries. Please ask me about accounts, loans, transfers, credit cards, or other banking services. How can I assist you with your banking needs?"
    
    print("[FILTER] ✓ Banking-related query detected")
    
    response = generate_bot_response_ollama(user_input)
    
    # If Ollama fails (returns None or error message), fall back to keyword matching
    if response is None or not response or "error" in response.lower() or "unable" in response.lower():
        print("[FALLBACK] Ollama unavailable, using static knowledge base")
        user_input_lower = user_input.lower()
        keywords = {
            "balance": "balance",
            "account": "account",
            "transaction": "transaction",
            "loan": "loan",
            "credit": "credit card",
            "transfer": "transfer",
            "password": "password",
            "support": "support",
            "help": "support"
        }
        
        for keyword, category in keywords.items():
            if keyword in user_input_lower:
                responses = BANKING_RESPONSES.get(category, BANKING_RESPONSES["support"])
                selected = random.choice(responses)
                print(f"[FALLBACK] Keyword match: '{keyword}' → {category}")
                return selected
        
        default_responses = [
            "That's a great question! How can I help you with your banking needs?",
            "I'm here to help! Would you like information about accounts, loans, transfers, or something else?",
            "Thank you for reaching out! Could you please provide more details about your inquiry?"
        ]
        selected = random.choice(default_responses)
        print(f"[FALLBACK] No keyword match, using default response")
        return selected
    
    print("[OLLAMA] ✓ Using Ollama response")
    return response

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': user_id,
            'username': username
        }), 201
    
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """Login user."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user_id': user['id'],
        'username': user['username']
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message and get a response."""
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({'error': 'user_id and message required'}), 400
    
    # Generate response
    response = generate_bot_response(message)
    
    # Store in database
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO chat_history (user_id, message, response, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, message, response, timestamp)
        )
        conn.commit()
        chat_id = cursor.lastrowid
        
        print(f"Chat stored successfully - ID: {chat_id}, User: {user_id}, Timestamp: {timestamp}")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'chat_id': chat_id,
            'message': message,
            'response': response,
            'timestamp': timestamp
        }), 200
    
    except Exception as e:
        print(f"Error storing chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    """Get chat history for a user."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'message': row['message'],
                'response': row['response'],
                'timestamp': row['timestamp']
            })
        
        print(f"Retrieved {len(history)} chat messages for user {user_id}")
        
        return jsonify({
            'success': True,
            'history': history
        }), 200
    
    except Exception as e:
        print(f"Error retrieving history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status including Ollama connection."""
    ollama_base_url = "http://localhost:11434"
    
    try:
        ollama_response = requests.get(ollama_base_url, timeout=2)
        ollama_running = ollama_response.status_code == 200
    except:
        ollama_running = False
    
    # Get available Ollama models
    ollama_models = []
    if ollama_running:
        try:
            models_response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
            if models_response.status_code == 200:
                models_data = models_response.json().get("models", [])
                ollama_models = [m.get("name", "Unknown") for m in models_data]
        except:
            pass
    
    return jsonify({
        'backend': 'running',
        'ollama': {
            'running': ollama_running,
            'api_url': ollama_base_url,
            'model': OLLAMA_MODEL,
            'available_models': ollama_models
        },
        'database': 'connected'
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'Backend is running'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

