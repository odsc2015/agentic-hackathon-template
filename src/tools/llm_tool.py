import json
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ConfigDict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import Config


logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    user_id: str
    message: str
    timestamp: datetime


class EventDetectionResult(BaseModel):
    agreement_detected: bool
    event_summary: str
    event_datetime: str
    participants: List[str]
    location: Optional[str] = None
    event_type: Optional[str] = None
    confidence: float = 0.0
    source_message: str

    @property
    def event_datetime_obj(self) -> datetime:
        return datetime.fromisoformat(self.event_datetime.replace('Z', '+00:00'))


class GeminiAnalyzer:
    def __init__(self):
        Config.validate_config()

        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.system_prompt = self._get_system_prompt()

        logger.info("Gemini Client initialized")
    
    @staticmethod
    def _get_system_prompt() -> str:
        return """
        You are an AI assistant specialized in analyzing chat conversations to detect agreements, plans, and scheduled events. 
        Your task is to identify when people agree to meet, schedule events, or make plans.

        ## TASK BREAKDOWN
        1. **Scan the conversation** for explicit agreements or clear plans
        2. **Extract key information**: event summary, date/time, participants, location, event type
        3. **Calculate confidence** based on clarity of agreement (0.0-1.0)
        4. **Identify the source message** that triggered the detection
        5. **Return structured JSON** with all extracted information
        
        ## DETECTION GUIDELINES
        
        ### WHAT TO DETECT (Explicit agreements):
        - "Let's meet tomorrow at 3 PM"
        - "How about lunch on Friday?"
        - "We should have a call next week"
        - "Team meeting at 2 PM today"
        - "Dinner tonight at 7 PM"
        - "Perfect! Let's schedule it"
        - "That works for me"
        - "I can make it too"
        
        ### WHAT NOT TO DETECT:
        - General discussions without specific plans
        - Past events or completed activities
        - Vague statements like "we should meet sometime"
        - Individual plans not involving others
        - Casual conversations about weekends, hobbies, etc.
        
        ## SPECIFIC INSTRUCTIONS
        
        ### Date/Time Processing:
        - Convert relative times: "tomorrow" → next day, "next week" → following week
        - Handle time zones: assume local time if not specified
        - Format as ISO 8601: YYYY-MM-DDTHH:MM:SS
        - If only time given: assume today or next occurrence
        
        ### Participant Detection:
        - Include all usernames mentioned in the conversation
        - Look for agreement confirmations: "works for me", "I can make it", "perfect"
        - Don't include participants who didn't respond
        
        ### Event Classification:
        - meeting: formal team/group meetings
        - call: phone/video calls
        - lunch/dinner: social meals
        - appointment: one-on-one meetings
        - other: miscellaneous events
        
        ### Confidence Scoring:
        - 0.9-1.0: Clear agreement with specific time/date
        - 0.7-0.8: Agreement with approximate time
        - 0.5-0.6: Tentative agreement
        - 0.0-0.4: No clear agreement
        
        ### Source Message Selection:
        - Choose the most informative message that contains key details
        - Prefer messages with specific time/date information
        - Avoid generic responses like "ok" or "sure"
        
        ## OUTPUT FORMAT
        Return ONLY valid JSON matching the EventDetectionResult schema. 
        If no agreement is detected, set agreement_detected to false and leave other fields empty or null.
        """
    
    def analyze_chat(self, chat_history: List[ChatMessage]) -> Optional[EventDetectionResult]:
        try:
            if not chat_history:
                logger.warning("Empty chat history provided")
                return None

            formatted_history = self._format_chat_history(chat_history)
            prompt = f"""Analyze the following chat conversation and detect any agreements or scheduled events:\n\n{formatted_history}"""

            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    response_mime_type="application/json",
                    response_schema=EventDetectionResult,
                )
            )

            if response.parsed and response.parsed.agreement_detected:
                return response.parsed
            
            logger.info("No agreement detected in chat history")
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing chat: {e}")
            return None

    @staticmethod
    def _format_chat_history(chat_history: List[ChatMessage]) -> str:
        formatted_messages = []
        
        for msg in chat_history:
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted_messages.append(f"[{timestamp}] {msg.user_id}: {msg.message}")
        
        return "\n".join(formatted_messages)
    
    def analyze_chat_simple(self, messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        try:
            chat_messages = []
            for msg in messages:
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
                    message=msg['message'],
                    timestamp=timestamp
                )
                chat_messages.append(chat_message)

            event = self.analyze_chat(chat_messages)
            
            if event:
                return {
                    'agreement_detected': event.agreement_detected,
                    'event_summary': event.event_summary,
                    'event_datetime': event.event_datetime,
                    'event_datetime_obj': event.event_datetime_obj,
                    'participants': event.participants,
                    'location': event.location,
                    'event_type': event.event_type,
                    'confidence': event.confidence,
                    'source_message': event.source_message
                }
            
            return {'agreement_detected': False}
            
        except Exception as e:
            logger.error(f"Error in analyze_chat_simple: {e}")
            return None


def analyze_chat(messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    analyzer = GeminiAnalyzer()

    return analyzer.analyze_chat_simple(messages)


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
