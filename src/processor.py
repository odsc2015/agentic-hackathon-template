import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from db_handler import DatabaseHandler
from tools.llm_tool import analyze_chat
from config import Config

# Configure logging
logger = logging.getLogger(__name__)


class ChatProcessor:
    """Processes chat messages to detect and save events to the database."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the chat processor.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self.db_handler = DatabaseHandler(self.db_path)
        self.confidence_threshold = 0.8
        
        logger.info(f"Chat processor initialized with confidence threshold: {self.confidence_threshold}")
    
    def process_chat_messages(self, messages: List[Dict[str, Any]], 
                            source_chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Process chat messages to detect events and save them to the database.
        
        Args:
            messages: List of message dictionaries with keys: user_id, username, message, timestamp
            source_chat_id: ID of the chat where the messages originated
            
        Returns:
            Dictionary with processing results, or None if no event was detected/saved
        """
        try:
            if not messages:
                logger.warning("No messages provided for processing")
                return None
            
            # Analyze chat messages using Gemini
            logger.info(f"Analyzing {len(messages)} messages from chat {source_chat_id}")
            analysis_result = analyze_chat(messages)
            
            if not analysis_result:
                logger.info("No analysis result returned from Gemini")
                return None
            
            if not analysis_result.get('agreement_detected'):
                logger.info("No agreement detected in chat messages")
                return None
            
            # Check confidence threshold
            confidence = analysis_result.get('confidence', 0.0)
            if confidence < self.confidence_threshold:
                logger.info(f"Confidence {confidence} below threshold {self.confidence_threshold}, skipping event creation")
                return {
                    'event_detected': True,
                    'confidence': confidence,
                    'threshold_met': False,
                    'message': f"Event detected but confidence {confidence} below threshold {self.confidence_threshold}"
                }
            
            # Calculate reminder times
            event_datetime = datetime.fromisoformat(analysis_result['event_datetime'].replace('Z', '+00:00'))
            reminder_1_dt = self._calculate_reminder_time(event_datetime, Config.DEFAULT_REMINDER_OFFSETS['reminder_1'])
            reminder_2_dt = self._calculate_reminder_time(event_datetime, Config.DEFAULT_REMINDER_OFFSETS['reminder_2'])
            
            # Get the primary user (first participant or message sender)
            primary_user_id = self._get_primary_user_id(messages, analysis_result.get('participants', []))
            
            # Save event to database
            event_id = self.db_handler.add_event(
                user_id=primary_user_id,
                source_chat_id=source_chat_id,
                event_summary=analysis_result['event_summary'],
                event_dt=event_datetime,
                reminder_1_dt=reminder_1_dt,
                reminder_2_dt=reminder_2_dt
            )
            
            logger.info(f"Event saved to database with ID: {event_id}")
            
            return {
                'event_detected': True,
                'confidence': confidence,
                'threshold_met': True,
                'event_id': event_id,
                'event_summary': analysis_result['event_summary'],
                'event_datetime': analysis_result['event_datetime'],
                'participants': analysis_result.get('participants', []),
                'location': analysis_result.get('location'),
                'event_type': analysis_result.get('event_type'),
                'reminder_1_dt': reminder_1_dt.isoformat() if reminder_1_dt else None,
                'reminder_2_dt': reminder_2_dt.isoformat() if reminder_2_dt else None,
                'message': f"Event successfully saved with ID {event_id}"
            }
            
        except Exception as e:
            logger.error(f"Error processing chat messages: {e}")
            return {
                'error': True,
                'message': f"Error processing chat messages: {str(e)}"
            }
    
    def _calculate_reminder_time(self, event_datetime: datetime, offset_minutes: int) -> Optional[datetime]:
        """
        Calculate reminder time based on event time and offset.
        
        Args:
            event_datetime: The event datetime
            offset_minutes: Minutes before the event to send reminder
            
        Returns:
            Reminder datetime or None if offset is invalid
        """
        try:
            if offset_minutes <= 0:
                return None
            
            reminder_time = event_datetime - timedelta(minutes=offset_minutes)
            
            # Don't set reminders in the past
            if reminder_time <= datetime.now():
                logger.warning(f"Calculated reminder time {reminder_time} is in the past, skipping")
                return None
            
            return reminder_time
            
        except Exception as e:
            logger.error(f"Error calculating reminder time: {e}")
            return None
    
    def _get_primary_user_id(self, messages: List[Dict[str, Any]], 
                           participants: List[str]) -> str:
        """
        Determine the primary user ID for the event.
        
        Args:
            messages: List of chat messages
            participants: List of participant usernames from analysis
            
        Returns:
            Primary user ID
        """
        try:
            # If we have participants from analysis, try to match with message senders
            if participants and messages:
                for msg in messages:
                    if msg.get('username') in participants:
                        return msg.get('user_id', 'unknown')
            
            # Fallback to the first message sender
            if messages:
                return messages[0].get('user_id', 'unknown')
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error determining primary user ID: {e}")
            return 'unknown'
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics from the database.
        
        Returns:
            Dictionary with processing statistics
        """
        try:
            db_stats = self.db_handler.get_database_stats()
            return {
                'database_stats': db_stats,
                'confidence_threshold': self.confidence_threshold,
                'processor_status': 'active'
            }
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {'error': str(e)}


# Convenience function for direct usage
def process_chat(messages: List[Dict[str, Any]], source_chat_id: str) -> Optional[Dict[str, Any]]:
    """
    Process chat messages and save events to database if confidence threshold is met.
    
    Args:
        messages: List of message dictionaries with keys: user_id, username, message, timestamp
        source_chat_id: ID of the chat where the messages originated
        
    Returns:
        Dictionary with processing results, or None if no event was detected/saved
    """
    processor = ChatProcessor()
    return processor.process_chat_messages(messages, source_chat_id)


# Example usage and testing
if __name__ == "__main__":
    # Example test
    from datetime import datetime, timedelta
    
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
    
    result = process_chat(test_messages, "chat123")
    print(f"Processing result: {result}") 