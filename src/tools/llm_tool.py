import google.generativeai as genai
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import sys
import os
from pydantic import BaseModel, Field, ConfigDict


# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import Config

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    user_id: str
    username: str
    message: str
    timestamp: datetime
    # message_id: str


@dataclass
class ExtractedEvent:
    """Represents an extracted event from chat analysis."""
    event_summary: str
    event_datetime: datetime
    participants: List[str]
    location: Optional[str] = None
    event_type: Optional[str] = None
    confidence: float = 0.0
    source_message: str = ""


class GeminiAnalyzer:
    """Gemini API wrapper for analyzing chat messages and extracting events."""
    
    def __init__(self):
        """Initialize the Gemini analyzer with API configuration."""
        Config.validate_config()
        
        # Configure Gemini API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        # Define the system prompt for event extraction
        self.system_prompt = self._get_system_prompt()
        
        logger.info(f"Gemini analyzer initialized with model: {Config.GEMINI_MODEL}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for event extraction."""
        return """
You are an AI assistant specialized in analyzing chat conversations to detect agreements, plans, and scheduled events. 
Your task is to identify when people agree to meet, schedule events, or make plans.

IMPORTANT: Only respond with valid JSON. If no agreement or event is detected, return {"agreement_detected": false}.

When you detect an agreement or event, respond with this exact JSON structure:

{
    "agreement_detected": true,
    "event_summary": "Brief description of the event/meeting",
    "event_datetime": "YYYY-MM-DD HH:MM:SS",
    "participants": ["username1", "username2"],
    "location": "meeting location if mentioned",
    "event_type": "meeting/lunch/dinner/call/etc",
    "confidence": 0.95,
    "source_message": "The specific message that triggered this detection"
}

Guidelines:
1. Only detect explicit agreements or clear plans
2. Extract exact dates and times when possible
3. Include all participants mentioned in the conversation
4. Set confidence based on how clear the agreement is (0.0-1.0)
5. If time is mentioned without date, assume today or next occurrence
6. Handle relative times like "tomorrow", "next week", "in 2 hours"
7. For recurring events, extract the next occurrence
8. If location is mentioned, include it
9. Categorize the event type appropriately

Examples of what to detect:
- "Let's meet tomorrow at 3 PM"
- "How about lunch on Friday?"
- "We should have a call next week"
- "Team meeting at 2 PM today"
- "Dinner tonight at 7 PM"

Examples of what NOT to detect:
- General discussions without specific plans
- Past events
- Vague statements like "we should meet sometime"
- Individual plans not involving others
"""
    
    def analyze_chat(self, chat_history: List[ChatMessage]) -> Optional[ExtractedEvent]:
        """
        Analyze chat history to detect agreements and extract event information.
        
        Args:
            chat_history: List of ChatMessage objects representing the conversation
            
        Returns:
            ExtractedEvent object if agreement is detected, None otherwise
        """
        try:
            if not chat_history:
                logger.warning("Empty chat history provided")
                return None
            
            # Format chat history for analysis
            formatted_history = self._format_chat_history(chat_history)
            
            # Create the prompt for analysis
            prompt = f"""
{self.system_prompt}

Analyze the following chat conversation and detect any agreements or scheduled events:

{formatted_history}

Respond only with valid JSON.
"""
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Parse the response
            result = self._parse_gemini_response(response.text)
            
            if result and result.get('agreement_detected'):
                return self._create_extracted_event(result, chat_history)
            
            logger.info("No agreement detected in chat history")
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing chat: {e}")
            return None
    
    def _format_chat_history(self, chat_history: List[ChatMessage]) -> str:
        """Format chat history for analysis."""
        formatted_messages = []
        
        for msg in chat_history:
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted_messages.append(f"[{timestamp}] {msg.username}: {msg.message}")
        
        return "\n".join(formatted_messages)
    
    def _parse_gemini_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse the JSON response from Gemini."""
        try:
            # Clean the response text (remove markdown formatting if present)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            result = json.loads(cleaned_text)
            logger.debug(f"Parsed Gemini response: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return None
    
    def _create_extracted_event(self, result: Dict[str, Any], chat_history: List[ChatMessage]) -> ExtractedEvent:
        """Create an ExtractedEvent object from the parsed result."""
        try:
            # Parse the datetime
            event_datetime = datetime.fromisoformat(result['event_datetime'].replace('Z', '+00:00'))
            
            # Create the extracted event
            event = ExtractedEvent(
                event_summary=result.get('event_summary', ''),
                event_datetime=event_datetime,
                participants=result.get('participants', []),
                location=result.get('location'),
                event_type=result.get('event_type'),
                confidence=result.get('confidence', 0.0),
                source_message=result.get('source_message', '')
            )
            
            logger.info(f"Extracted event: {event.event_summary} at {event.event_datetime}")
            return event
            
        except Exception as e:
            logger.error(f"Error creating extracted event: {e}")
            raise
    
    def analyze_chat_simple(self, messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Simplified version of analyze_chat that takes a list of message dictionaries.
        This is a convenience method for easier integration.
        
        Args:
            messages: List of message dictionaries with keys: user_id, username, message, timestamp
            
        Returns:
            Dictionary with event information if detected, None otherwise
        """
        try:
            # Convert message dictionaries to ChatMessage objects
            chat_messages = []
            for msg in messages:
                # Handle different timestamp formats
                timestamp = msg['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    pass
                else:
                    logger.warning(f"Unsupported timestamp format: {timestamp}")
                    continue
                
                chat_message = ChatMessage(
                    user_id=msg['user_id'],
                    username=msg['username'],
                    message=msg['message'],
                    timestamp=timestamp
                )
                chat_messages.append(chat_message)
            
            # Analyze using the main method
            extracted_event = self.analyze_chat(chat_messages)
            
            if extracted_event:
                return {
                    'agreement_detected': True,
                    'event_summary': extracted_event.event_summary,
                    'event_datetime': extracted_event.event_datetime.isoformat(),
                    'participants': extracted_event.participants,
                    'location': extracted_event.location,
                    'event_type': extracted_event.event_type,
                    'confidence': extracted_event.confidence,
                    'source_message': extracted_event.source_message
                }
            
            return {'agreement_detected': False}
            
        except Exception as e:
            logger.error(f"Error in analyze_chat_simple: {e}")
            return None


# Convenience function for direct usage
def analyze_chat(messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Analyze chat messages to detect agreements and extract event information.
    
    Args:
        messages: List of message dictionaries with keys: user_id, username, message, timestamp
        
    Returns:
        Dictionary with event information if detected, None otherwise
    """
    analyzer = GeminiAnalyzer()
    return analyzer.analyze_chat_simple(messages)


# Example usage and testing
if __name__ == "__main__":
    # Example test
    test_messages = [
        {
            'user_id': 'user1',
            'username': 'Alice',
            'message': 'Hey team, should we have a meeting tomorrow at 3 PM?',
            'timestamp': datetime.now()
        },
        {
            'user_id': 'user2',
            'username': 'Bob',
            'message': 'That works for me!',
            'timestamp': datetime.now()
        },
        {
            'user_id': 'user3',
            'username': 'Charlie',
            'message': 'I can make it too.',
            'timestamp': datetime.now()
        }
    ]
    
    result = analyze_chat(test_messages)
    print(f"Analysis result: {json.dumps(result, indent=2, default=str)}")
