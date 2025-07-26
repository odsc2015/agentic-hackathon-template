import asyncio
import logging
import signal
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from tools.telegram_bot_tool import TelegramBot, TelegramMessenger
from scheduler import ReminderScheduler
from processor import ChatProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramIntegration:
    def __init__(self):
        self.telegram_bot = None
        self.telegram_messenger = None
        self.scheduler = None
        self.processor = ChatProcessor()
        self.running = False
        self.monitoring_task = None

        Config.validate_config()

        logger.info("Telegram integration initialized")
    
    async def start(self):
        try:
            logger.info("Starting Telegram integration...")

            self.telegram_bot = TelegramBot()
            await self.telegram_bot.start()

            self.telegram_messenger = TelegramMessenger()
            await self.telegram_messenger.initialize()

            self.scheduler = ReminderScheduler()
            self.scheduler.set_messenger(self.telegram_messenger)
            self.scheduler.start()

            self.telegram_bot.set_message_callback(self._process_message)

            self.running = True
            self.monitoring_task = asyncio.create_task(self._monitor_and_report())
            
            logger.info("Telegram integration started successfully")

            bot_info = await self.telegram_bot.get_bot_info()
            logger.info(f"Bot info: {bot_info}")
            
        except Exception as e:
            logger.error(f"Error starting Telegram integration: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        try:
            logger.info("Stopping Telegram integration...")
            
            self.running = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            if self.scheduler:
                self.scheduler.stop()
            
            if self.telegram_bot:
                await self.telegram_bot.stop()
            
            if self.telegram_messenger:
                await self.telegram_messenger.close()
            
            logger.info("Telegram integration stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Telegram integration: {e}")
    
    async def _process_message(self, messages: List[Dict[str, Any]], chat_id: str):
        try:
            logger.info(f"Processing {len(messages)} messages from chat {chat_id}")

            result = self.processor.process_chat_messages(messages, chat_id)
            
            if result and result.get('event_detected'):
                logger.info(f"Event detected: {result.get('event_summary', 'N/A')}")

                if self.telegram_bot:
                    confirmation_msg = f"✅ Event detected and scheduled: {result.get('event_summary', 'N/A')}"
                    await self.telegram_bot.send_message(chat_id, confirmation_msg)
            else:
                logger.debug("No event detected in messages")
                
        except Exception as e:
            logger.error(f"Error processing messages: {e}")
    
    async def _monitor_and_report(self):
        while self.running:
            try:
                stats = self.telegram_bot.get_chat_history_stats()
                
                if stats['total_messages'] > 0:
                    logger.info(f"📊 Chat History Status: {stats['total_chats']} chats, {stats['total_messages']} total messages")
                    for chat_id, details in stats['chat_details'].items():
                        if details['percentage_full'] > 50:
                            logger.info(f"   Chat {chat_id}: {details['message_count']}/{Config.MAX_CHAT_HISTORY} messages ({details['percentage_full']:.1f}% full)")

                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                logger.info("Monitoring task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring task: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        try:
            await self.start()

            logger.info("🤖 Telegram bot is running...")
            logger.info(f"   Monitoring chats every {Config.MAX_CHAT_HISTORY} messages")
            logger.info("   Press Ctrl+C to stop")

            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.stop()


def setup_signal_handlers(integration: TelegramIntegration):
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(integration.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    try:
        integration = TelegramIntegration()
        setup_signal_handlers(integration)
        await integration.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
