# AI-Powered Event Reminder System with Telegram Integration

An intelligent event detection and reminder system that uses Google Gemini AI to analyze Telegram group chat conversations and automatically schedule reminders. Features advanced chat history management for efficient message processing.

## 🎯 Overview

This system automatically detects when people agree to meet or schedule events in Telegram group chats, then sends timely reminders to participants. It combines:

- **AI Analysis**: Google Gemini AI analyzes chat messages to detect event agreements
- **Chat History Management**: Intelligent message batching with configurable thresholds
- **Real-time Processing**: Listens to Telegram group messages and processes them efficiently
- **Smart Scheduling**: Automatically calculates reminder times and schedules notifications
- **Telegram Integration**: Sends reminders directly via Telegram private messages

## 🏗️ Architecture

The system follows a modular architecture with these key components:

1. **Telegram Bot**: Listens to group messages and manages chat histories
2. **Chat History Manager**: Collects messages until threshold is reached
3. **AI Processor**: Analyzes message batches using Gemini AI to detect events
4. **Database**: Stores events, reminders, and message history
5. **Scheduler**: Regularly checks for due reminders
6. **Notifier**: Sends private Telegram messages to users

## 🚀 Features

- **Intelligent Event Detection**: Uses Gemini AI to understand natural language event agreements
- **Chat History Management**: Processes messages in configurable batches (default: 3 messages)
- **Real-time Monitoring**: Monitors Telegram groups and processes messages efficiently
- **Automatic Reminders**: Sends two-tier reminder system (2 hours and 2 days before events)
- **Group Confirmation**: Sends confirmation messages when events are detected
- **Configurable Thresholds**: Adjust message batch sizes and processing frequency
- **Memory Management**: Automatic cleanup of processed chat histories
- **Robust Error Handling**: Graceful handling of API errors and network issues

## 📋 Prerequisites

- Python 3.10+
- Telegram Bot Token (from @BotFather)
- Google Gemini API Key

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ji
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   DATABASE_PATH=events.db
   MAX_CHAT_HISTORY=3
   LOG_LEVEL=INFO
   ```

5. **Create a Telegram bot**:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Disable group privacy in bot settings
   - Add bot to your groups

## 🚀 Quick Start

1. **Run the full system**:
   ```bash
   python run_telegram_bot.py
   ```

2. **Start chatting in your groups**:
   - The bot will collect messages in chat histories
   - When `MAX_CHAT_HISTORY` is reached, it processes the batch
   - Users will receive private reminders before events

## 📖 Usage Examples

### Group Chat Example
```
User A: "Let's meet tomorrow at 3 PM for coffee"
User B: "Sounds good! I'll be there"
User C: "I can make it too"
[After 3 messages...]
Bot: "✅ Event detected and scheduled: Coffee meeting tomorrow at 3 PM"
```

### Reminder Messages
Users receive private messages like:
- "🔔 Reminder: in 2 days you have 'Coffee meeting' on 2024-01-16 at 15:00"
- "⏰ Final Reminder: You have 'Coffee meeting' on 2024-01-16 at 15:00 (in 2 hours)"

## 📁 Project Structure

```
ji/
├── src/
│   ├── config.py              # Configuration management
│   ├── processor.py           # Message processing logic
│   ├── scheduler.py           # Reminder scheduling
│   ├── db_handler.py          # Database operations
│   ├── tools/
│   │   ├── telegram_bot_tool.py    # Telegram integration with chat history
│   │   └── llm_tool.py        # Gemini AI integration
├── run_telegram_bot.py        # Main bot runner with monitoring
├── test_chat_history.py       # Chat history testing
├── test_telegram_integration.py # Integration tests
├── CHAT_HISTORY_GUIDE.md      # Detailed chat history documentation
├── requirements.txt           # Dependencies
└── events.db                  # SQLite database
```

## 🔧 Configuration

### Chat History Management
Adjust in environment variables:
```env
MAX_CHAT_HISTORY=3  # Process every  messages
```

### Reminder Timing
Adjust in `src/config.py`:
```python
DEFAULT_REMINDER_OFFSETS = {
    'reminder_1': 120,  # 2 hours before event
    'reminder_2': 2880    # 2 days before event
}
```


### AI Confidence
Adjust detection sensitivity:
```python
confidence_threshold = 0.8  # In processor.py
```

