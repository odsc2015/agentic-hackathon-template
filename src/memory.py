import sqlite3
import os
from google import genai
from google.genai import types

class MemoryManager:
    def __init__(self, db_path="kiran_memory.db"):
        self.db_path = db_path
        # Ensure the database and table exist
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS interactions (id INTEGER PRIMARY KEY, user_input TEXT, agent_response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        self.conn.commit()
        # Initialize a Gemini client here as well for convenience (so executor can use memory.gemini_client)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise RuntimeError("Gemini API key not set in environment.")
        self.gemini_client = genai.Client(api_key=api_key)
    
    def save_interaction(self, user_input, agent_response):
        """Save the latest interaction to the SQLite database."""
        self.conn.execute(
            "INSERT INTO interactions (user_input, agent_response) VALUES (?, ?)",
            (user_input, agent_response)
        )
        self.conn.commit()
    
    def fetch_last_interaction(self):
        """Retrieve the most recent interaction (user_input and response) from memory, formatted for context."""
        cursor = self.conn.execute(
            "SELECT user_input, agent_response FROM interactions ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            last_user, last_agent = row
            # Return a brief summary of last interaction to use in prompts
            return f"Previously, the user said \"{last_user}\" and the agent replied \"{last_agent}\"."
        return None
