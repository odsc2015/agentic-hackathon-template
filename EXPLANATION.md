# Technical Explanation

## Agent Workflow

### Step-by-Step Processing Flow

1. **Message Reception**
   - Telegram bot receives messages from monitored groups
   - Messages are validated and filtered (text only, non-command)
   - Each message is added to chat-specific history

2. **Chat History Management**
   - Messages accumulate in per-chat histories
   - System tracks message count for each chat
   - When `MAX_CHAT_HISTORY` threshold is reached, processing is triggered

3. **Batch Processing**
   - Complete chat history is copied and cleared
   - Message batch is prepared for AI analysis
   - Processing happens asynchronously to avoid blocking new messages

4. **AI Analysis (Gemini)**
   - Structured prompt sent to Gemini AI
   - AI analyzes conversation for event agreements
   - Returns structured JSON with event details, confidence, participants

5. **Event Validation**
   - Confidence score checked against threshold (default: 0.8)
   - Event datetime parsed and validated
   - Participant list extracted and validated

6. **Database Storage**
   - Event details stored in SQLite database
   - Reminder times calculated (2 hours and 30 minutes before event)
   - Primary user identified for event ownership

7. **Reminder Scheduling**
   - Reminders added to scheduler queue
   - System monitors for due reminders
   - Notifications sent via private Telegram messages

## Key Modules

### Planner (`telegram_bot_tool.py`)
- **Purpose**: Manages message flow and processing triggers
- **Key Functions**:
  - `_add_message_to_history()`: Accumulates messages per chat
  - `_process_chat_history()`: Triggers batch processing
  - `get_chat_history_stats()`: Provides monitoring data

### Executor (`processor.py`)
- **Purpose**: Executes AI analysis and event processing
- **Key Functions**:
  - `process_chat_messages()`: Main processing pipeline
  - `_calculate_reminder_time()`: Computes reminder schedules
  - `_get_primary_user_id()`: Identifies event owner

### Memory Store (`db_handler.py`)
- **Purpose**: Persistent storage and data management
- **Key Functions**:
  - `add_event()`: Stores detected events
  - `get_due_reminders()`: Retrieves pending notifications
  - `add_message()`: Stores message history

## Tool Integration

### Google Gemini API
- **Function**: `analyze_chat(messages)`
- **Purpose**: Natural language understanding and event extraction
- **Input**: List of message dictionaries with user, content, timestamp
- **Output**: Structured JSON with event details, confidence, participants
- **Error Handling**: Retry logic for API failures, fallback responses

### Telegram Bot API
- **Function**: Message reception and sending
- **Purpose**: Real-time communication with users
- **Features**: Group message listening, private message sending
- **Rate Limiting**: Respects Telegram's API limits

### SQLite Database
- **Function**: Local data persistence
- **Purpose**: Store events, messages, and reminder schedules
- **Tables**: Events, Messages, Reminders
- **Operations**: CRUD operations with transaction support

## Reasoning Process

### Event Detection Logic
1. **Context Analysis**: AI examines conversation flow and context
2. **Agreement Detection**: Identifies when multiple users agree to meet
3. **DateTime Extraction**: Parses natural language time expressions
4. **Participant Identification**: Maps usernames to user IDs
5. **Confidence Scoring**: Assigns confidence based on clarity and agreement

### Decision Making
- **Threshold-based**: Only processes events above confidence threshold
- **Context-aware**: Considers conversation flow and user interactions
- **Validation-driven**: Multiple validation steps before event creation
- **Error-tolerant**: Graceful handling of parsing and API errors

### Memory Usage
- **In-Memory**: Chat histories stored per chat (configurable size)
- **Persistent**: Events and reminders in SQLite database
- **Cleanup**: Automatic cleanup of processed chat histories
- **Efficiency**: Memory usage scales with active chat count

## Planning Style

### Batch Processing Strategy
- **Threshold-driven**: Process when message count reaches limit
- **Asynchronous**: Non-blocking processing to maintain responsiveness
- **Chat-specific**: Independent processing per chat group
- **Configurable**: Adjustable batch sizes via environment variables

### Error Recovery
- **Graceful Degradation**: System continues operating despite errors
- **Retry Logic**: Automatic retries for transient failures
- **Fallback Mechanisms**: Alternative processing paths when primary fails
- **Logging**: Comprehensive error tracking and debugging

## Observability & Testing

### Logging Strategy
- **Structured Logging**: Consistent log format across components
- **Log Levels**: DEBUG, INFO, WARNING, ERROR with appropriate filtering
- **Log Files**: Separate files for bot operations and scheduler
- **Performance Tracking**: Processing times and success rates

### Monitoring Points
- **Message Processing Rate**: Messages processed per minute
- **AI Analysis Success**: Percentage of successful event detections
- **Database Performance**: Query times and operation success rates
- **Reminder Delivery**: Success rate of notification delivery
- **Error Frequency**: Types and frequency of system errors

### Testing Framework
- **Unit Tests**: Individual component testing (`test_processor.py`, `test_db.py`)
- **Integration Tests**: End-to-end system testing (`test_integration.py`)
- **Chat History Tests**: Message batching and processing tests
- **Mock Testing**: Simulated API responses for reliable testing

### Debugging Tools
- **Log Analysis**: Detailed logs for troubleshooting
- **Statistics Reporting**: Real-time system statistics
- **Force Processing**: Manual trigger for chat processing
- **Database Inspection**: Direct database access for debugging

