import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # API Settings
    API_TIMEOUT = 30
    MAX_TOKENS = 1000
    
    # CORS Settings
    CORS_ORIGINS = ["*"]  # Allow all origins in development
    
    # NLP Settings
    SPACY_MODEL = "en_core_web_sm"
    SUMMARIZATION_MODEL = "facebook/bart-large-cnn"