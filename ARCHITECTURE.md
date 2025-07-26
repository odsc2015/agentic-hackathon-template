# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM GROUPS                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Group A   │  │   Group B   │  │   Group C   │            │
│  │             │  │             │  │             │            │
│  │ Messages    │  │ Messages    │  │ Messages    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              MESSAGE HANDLER                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Chat History│  │ Chat History│  │ Chat History│        │ │
│  │  │   Group A   │  │   Group B   │  │   Group C   │        │ │
│  │  │ [msg1,msg2] │  │ [msg1,msg2] │  │ [msg1,msg2] │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSOR                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              CHAT PROCESSOR                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Message     │  │ Confidence  │  │ Event       │        │ │
│  │  │ Validation  │  │ Threshold   │  │ Detection   │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI ANALYSIS                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              GEMINI AI                                      │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Natural     │  │ Structured  │  │ Event       │        │ │
│  │  │ Language    │  │ JSON        │  │ Extraction  │        │ │
│  │  │ Processing  │  │ Output      │  │ & Analysis  │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              SQLITE DATABASE                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Events      │  │ Messages    │  │ Reminders   │        │ │
│  │  │ Table       │  │ Table       │  │ Table       │        │ │
│  │  │             │  │             │  │             │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCHEDULER                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              REMINDER SCHEDULER                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Due         │  │ Reminder    │  │ Notification│        │ │
│  │  │ Reminders   │  │ Timing      │  │ Queue       │        │ │
│  │  │ Checker     │  │ Calculator  │  │ Manager     │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NOTIFICATIONS                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   User A    │  │   User B    │  │   User C    │            │
│  │             │  │             │  │             │            │
│  │ Private     │  │ Private     │  │ Private     │            │
│  │ Messages    │  │ Messages    │  │ Messages    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Telegram Bot (Message Handler)
- **Purpose**: Receives and manages group messages
- **Key Features**:
  - Real-time message listening
  - Chat-specific history management
  - Automatic batch processing triggers
  - Message validation and filtering

### 2. Chat History Manager
- **Purpose**: Collects messages until processing threshold
- **Key Features**:
  - Per-chat message accumulation
  - Configurable batch sizes (MAX_CHAT_HISTORY)
  - Automatic cleanup after processing
  - Memory-efficient storage

### 3. AI Processor (ChatProcessor)
- **Purpose**: Analyzes message batches for event detection
- **Key Features**:
  - Confidence threshold validation
  - Event datetime extraction
  - Participant identification
  - Reminder time calculation

### 4. Gemini AI Integration
- **Purpose**: Natural language understanding and event extraction
- **Key Features**:
  - Structured JSON output
  - Event agreement detection
  - DateTime parsing
  - Participant extraction

### 5. Database Handler
- **Purpose**: Persistent storage of events and messages
- **Key Features**:
  - SQLite database management
  - Event and reminder storage
  - Message history tracking
  - Statistics and reporting

### 6. Reminder Scheduler
- **Purpose**: Manages reminder timing and delivery
- **Key Features**:
  - Due reminder checking
  - Multi-tier reminder system
  - Notification queue management
  - Error handling and retries

## Data Flow

```
1. Message Reception
   ↓
2. Chat History Accumulation
   ↓
3. Threshold Check (MAX_CHAT_HISTORY)
   ↓
4. Batch Processing Trigger
   ↓
5. AI Analysis (Gemini)
   ↓
6. Event Detection & Validation
   ↓
7. Database Storage
   ↓
8. Reminder Scheduling
   ↓
9. Notification Delivery
```

## Memory Structure

### In-Memory Storage
- **Chat Histories**: Per-chat message lists
- **Processing Queues**: Pending analysis batches
- **Active Sessions**: Current bot states

### Persistent Storage
- **Events Table**: Event details and metadata
- **Messages Table**: Historical message storage
- **Reminders Table**: Scheduled notification data

## Tool Integrations

### External APIs
- **Telegram Bot API**: Message reception and sending
- **Google Gemini API**: Natural language processing
- **SQLite Database**: Local data persistence

### Internal Tools
- **Message Validator**: Input sanitization
- **DateTime Parser**: Event time extraction
- **Confidence Calculator**: AI result validation
- **Reminder Timer**: Notification scheduling

## Logging and Observability

### Log Levels
- **DEBUG**: Detailed processing steps
- **INFO**: Key system events
- **WARNING**: Potential issues
- **ERROR**: System failures

### Monitoring Points
- Message processing rates
- AI analysis success rates
- Database operation performance
- Reminder delivery status
- Error frequency and types

### Log Files
- `telegram_bot.log`: Bot operation logs
- `scheduler.log`: Reminder system logs
- Database logs: SQLite operation tracking

