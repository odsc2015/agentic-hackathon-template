import asyncio
import logging
import sys
import os
from typing import List, Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from tools.telegram_bot_tool import TelegramMessenger
from processor import ChatProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockTelegramMessenger:

    def __init__(self):
        self.sent_messages = []
        logger.info("Mock Telegram messenger initialized")
    
    async def initialize(self):
        logger.info("Mock Telegram messenger initialized")
    
    async def send_message(self, user_id: str, message: str) -> bool:
        self.sent_messages.append({
            'user_id': user_id,
            'message': message
        })
        logger.info(f"Mock: Sending message to {user_id}: {message}")
        return True
    
    async def close(self):
        logger.info("Mock Telegram messenger closed")


async def test_processor_integration():
    logger.info("Testing processor integration...")

    processor = ChatProcessor()
    mock_messages = [
        {
            'user_id': '123456789',
            'username': 'alice',
            'message': 'Let\'s meet tomorrow at 3 PM for coffee',
            'timestamp': '2024-01-15T10:00:00',
            'chat_id': '-987654321'
        },
        {
            'user_id': '987654321',
            'username': 'bob',
            'message': 'Sounds good! I\'ll be there',
            'timestamp': '2024-01-15T10:01:00',
            'chat_id': '-987654321'
        }
    ]

    result = processor.process_chat_messages(mock_messages, '-987654321')
    
    if result:
        logger.info(f"Processing result: {result}")
        return result.get('event_detected', False)
    else:
        logger.info("No event detected")
        return False


async def test_messenger_integration():
    logger.info("Testing messenger integration...")

    messenger = MockTelegramMessenger()
    await messenger.initialize()

    test_user_id = '123456789'
    test_message = 'Test reminder: Meeting tomorrow at 3 PM'
    
    success = await messenger.send_message(test_user_id, test_message)
    
    if success:
        logger.info("Message sent successfully")
        logger.info(f"Sent messages: {messenger.sent_messages}")
        return True
    else:
        logger.error("Failed to send message")
        return False


async def test_config_validation():
    logger.info("Testing configuration validation...")
    
    try:
        Config.validate_config()
        logger.info("Configuration validation passed")
        return True
    except ValueError as e:
        logger.warning(f"Configuration validation failed (expected): {e}")
        return False


async def test_full_integration():
    logger.info("Testing full integration flow...")

    config_ok = await test_config_validation()
    processor_ok = await test_processor_integration()
    messenger_ok = await test_messenger_integration()

    logger.info("=" * 50)
    logger.info("INTEGRATION TEST RESULTS:")
    logger.info(f"Configuration: {'✅ PASS' if config_ok else '⚠️  SKIP (no token)'}")
    logger.info(f"Processor: {'✅ PASS' if processor_ok else '❌ FAIL'}")
    logger.info(f"Messenger: {'✅ PASS' if messenger_ok else '❌ FAIL'}")
    logger.info("=" * 50)
    
    return config_ok and processor_ok and messenger_ok


async def main():
    try:
        logger.info("Starting Telegram integration tests...")
        
        # Run all tests
        success = await test_full_integration()
        
        if success:
            logger.info("All tests passed! 🎉")
        else:
            logger.warning("Some tests failed or were skipped")
        
        return success
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
