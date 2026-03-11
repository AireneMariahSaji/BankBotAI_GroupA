# BankBot Configuration File

# Backend Settings
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5000
DEBUG_MODE = True

# Frontend Settings
FRONTEND_HOST = "localhost"
FRONTEND_PORT = 8501

# Database Settings
DATABASE_PATH = "chatbot.db"
DATABASE_TYPE = "sqlite"

# API Settings
API_BASE_URL = "http://localhost:5000/api"
API_TIMEOUT = 30

# Security Settings
PASSWORD_HASH_METHOD = "werkzeug"
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FILE = "bankbot.log"

# Feature Flags
ENABLE_CHAT_HISTORY = True
ENABLE_USER_REGISTRATION = True
ENABLE_QUICK_ACTIONS = True

# Ollama Settings
OLLAMA_ENABLED = True
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "neural-chat:latest"  # Fast by default. Options: "neural-chat:latest" (5-10s), "mistral:latest" (10-15s), "orca-mini:latest" (3-5s)
OLLAMA_TIMEOUT = 60  # 60 seconds
