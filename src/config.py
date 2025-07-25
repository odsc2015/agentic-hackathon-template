import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application."""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'events.db')
    
    # Application Configuration
    MAX_CHAT_HISTORY = int(os.getenv('MAX_CHAT_HISTORY', '30'))
    DEFAULT_REMINDER_OFFSETS = {
        'reminder_1': 120,  # minutes before event
        'reminder_2': 2880   # minutes before event
    }
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        return True
