import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import Config
from processor import ChatProcessor

logger = logging.getLogger(__name__)


class TelegramBot:
    
    def __init__(self, bot_token: str = None, allowed_group_ids: List[str] = None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.application = None
        self.bot = None
        self.processor = ChatProcessor()
        self.message_callback = None
        self.chat_histories = {}
        
        if not self.bot_token:
            raise ValueError("Telegram bot token is required")
        
        logger.info("Telegram bot initialized")
    
    async def start(self):
        try:
            self.application = Application.builder().token(self.bot_token).build()
            self.bot = self.application.bot

            self.application.add_handler(
                MessageHandler(
                    filters.ChatType.GROUPS | filters.TEXT | ~filters.COMMAND,
                    self._handle_message
                )
            )

            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Telegram bot started successfully")
            
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
            raise
    
    async def stop(self):
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            logger.info("Telegram bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            message = update.message
            chat_id = str(message.chat_id)

            message_data = {
                'user_id': str(message.from_user.id),
                'username': message.from_user.username or message.from_user.first_name,
                'message': message.text,
                'timestamp': message.date.isoformat(),
                'chat_id': chat_id
            }
            
            logger.info(f"Received message from {message_data['username']} in chat {chat_id}")

            await self._add_message_to_history(chat_id, message_data)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _add_message_to_history(self, chat_id: str, message_data: Dict[str, Any]):
        try:
            if chat_id not in self.chat_histories:
                self.chat_histories[chat_id] = []
            
            self.chat_histories[chat_id].append(message_data)
            
            logger.debug(f"Added message to chat {chat_id} history. Current length: {len(self.chat_histories[chat_id])}")
            
            if len(self.chat_histories[chat_id]) >= Config.MAX_CHAT_HISTORY:
                logger.info(f"Chat history for {chat_id} reached maximum length ({Config.MAX_CHAT_HISTORY}). Processing messages...")
                
                chat_history = self.chat_histories[chat_id].copy()
                
                self.chat_histories[chat_id] = []
                
                await self._process_chat_history(chat_history, chat_id)
            
        except Exception as e:
            logger.error(f"Error adding message to history for chat {chat_id}: {e}")
    
    async def _process_chat_history(self, chat_history: List[Dict[str, Any]], chat_id: str):
        try:
            logger.info(f"Processing {len(chat_history)} messages from chat {chat_id}")
            
            if self.message_callback:
                await self.message_callback(chat_history, chat_id)
            else:
                result = self.processor.process_chat_messages(chat_history, chat_id)
                if result and result.get('event_detected'):
                    logger.info(f"Event detected and processed: {result.get('event_summary', 'N/A')}")
                    
                    if result.get('threshold_met', False):
                        confirmation_msg = f"✅ Event detected and scheduled: {result.get('event_summary', 'N/A')}"
                        await self.send_message(chat_id, confirmation_msg)
                else:
                    logger.debug("No event detected in chat history")
            
        except Exception as e:
            logger.error(f"Error processing chat history for {chat_id}: {e}")
    
    async def _get_chat_history(self, chat_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        try:
            if chat_id in self.chat_histories:
                return self.chat_histories[chat_id][-limit:] if len(self.chat_histories[chat_id]) > limit else self.chat_histories[chat_id]
            else:
                return []
            
        except Exception as e:
            logger.error(f"Error getting chat history for {chat_id}: {e}")
            return []
    
    async def send_message(self, user_id: str, message: str) -> bool:
        try:
            if not self.bot:
                logger.error("Bot not initialized")
                return False
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"Message sent successfully to user {user_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error sending message to {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message to {user_id}: {e}")
            return False
    
    def set_message_callback(self, callback: Callable):
        self.message_callback = callback
        logger.info("Message callback set")
    
    async def get_bot_info(self) -> Dict[str, Any]:
        try:
            if not self.bot:
                return {"error": "Bot not initialized"}
            
            me = await self.bot.get_me()
            return {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "can_join_groups": me.can_join_groups,
                "can_read_all_group_messages": me.can_read_all_group_messages
            }
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return {"error": str(e)}
    
    def get_chat_history_stats(self) -> Dict[str, Any]:
        stats = {
            'total_chats': len(self.chat_histories),
            'chats_with_messages': 0,
            'total_messages': 0,
            'chat_details': {}
        }
        
        for chat_id, history in self.chat_histories.items():
            message_count = len(history)
            stats['total_messages'] += message_count
            
            if message_count > 0:
                stats['chats_with_messages'] += 1
                stats['chat_details'][chat_id] = {
                    'message_count': message_count,
                    'percentage_full': (message_count / Config.MAX_CHAT_HISTORY) * 100
                }
        
        return stats
    
    def force_process_chat(self, chat_id: str) -> bool:
        try:
            if chat_id in self.chat_histories and self.chat_histories[chat_id]:
                logger.info(f"Force processing chat {chat_id} with {len(self.chat_histories[chat_id])} messages")
                
                chat_history = self.chat_histories[chat_id].copy()
                self.chat_histories[chat_id] = []
                
                asyncio.create_task(self._process_chat_history(chat_history, chat_id))
                return True
            else:
                logger.warning(f"No messages in chat history for {chat_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error force processing chat {chat_id}: {e}")
            return False


class TelegramMessenger:
    
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.bot = None
        
        if not self.bot_token:
            raise ValueError("Telegram bot token is required")
    
    async def initialize(self):
        try:
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram messenger initialized")
        except Exception as e:
            logger.error(f"Error initializing Telegram messenger: {e}")
            raise
    
    async def send_message(self, user_id: str, message: str) -> bool:
        try:
            if not self.bot:
                await self.initialize()
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"Message sent successfully to user {user_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error sending message to {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message to {user_id}: {e}")
            return False
    
    async def close(self):
        try:
            if self.bot:
                await self.bot.close()
            logger.info("Telegram messenger closed")
        except Exception as e:
            logger.error(f"Error closing Telegram messenger: {e}")


async def create_telegram_bot(bot_token: str = None, allowed_group_ids: List[str] = None) -> TelegramBot:
    bot = TelegramBot(bot_token, allowed_group_ids)
    await bot.start()
    return bot


async def create_telegram_messenger(bot_token: str = None) -> TelegramMessenger:
    messenger = TelegramMessenger(bot_token)
    await messenger.initialize()
    return messenger
