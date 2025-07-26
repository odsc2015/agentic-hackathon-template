import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

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
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        return True
