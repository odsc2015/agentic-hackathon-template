## 2. `ARCHITECTURE.md`

```markdown
# Architecture Overview

Below, sketch (ASCII, hand-drawn JPEG/PNG pasted in, or ASCII art) the high-level components of your agent.

life-witness-agent/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VoiceInterface.jsx          # Voice input/output UI component
│   │   │   ├── PhotoUpload.jsx             # Drag & drop photo upload interface
│   │   │   ├── MemoryTimeline.jsx          # Timeline view of life events
│   │   │   ├── MemoryCard.jsx              # Individual memory display card
│   │   │   └── AgentStatus.jsx             # Real-time agent activity indicator
│   │   ├── services/
│   │   │   ├── apiClient.js                # HTTP client for backend API calls
│   │   │   ├── voiceService.js             # Web Speech API wrapper
│   │   │   ├── uploadService.js            # File upload handling
│   │   │   └── websocketClient.js          # Real-time agent communication
│   │   ├── utils/
│   │   │   ├── audioUtils.js               # Audio processing utilities
│   │   │   ├── imageUtils.js               # Image compression/validation
│   │   │   └── formatters.js               # Data formatting helpers (optional)
│   │   ├── App.jsx                         # Main React application component
│   │   └── main.jsx                        # React app entry point
│   ├── public/
│   │   ├── index.html                      # HTML template
│   │   └── manifest.json                   # PWA manifest
│   ├── package.json                        # Frontend dependencies
│   └── vite.config.js                      # Vite build configuration (Or similar config file)
├── backend/
│   ├── agents/
│   │   ├── base_agent.py                   # Abstract base class for all agents (Should be implemented first)
│   │   ├── planner_agent.py                # Intent parsing and task planning
│   │   ├── voice_agent.py                  # Speech processing and TTS
│   │   ├── vision_agent.py                 # Image/video analysis via Gemini
│   │   ├── context_agent.py                # Gmail/Calendar data integration
│   │   ├── memory_agent.py                 # Memory storage and retrieval
│   │   ├── insight_agent.py                # Pattern recognition and analysis
│   │   └── response_agent.py               # Conversational response generation
│   ├── orchestration/
│   │   ├── orchestrator.py                 # Main agent coordination engine (using Langgraph or the execution engine)
│   │   ├── event_bus.py                    # Event-driven communication system (optional)
│   │   ├── task_queue.py                   # Async task management
│   │   └── agent_pool.py                   # Agent instance management
│   ├── services/
│   │   ├── gemini_service.py               # Gemini API client and utilities
│   │   ├── gmail_service.py                # Gmail API integration
│   │   ├── calendar_service.py             # Google Calendar API integration
│   │   └── storage_service.py              # File system and JSON persistence (Need other storage services like vertex or bigquery?)
│   ├── utils/
│   │   ├── logging_config.py               # Structured logging setup
│   │   ├── tracing.py                      # Distributed tracing utilities (Optional)
│   │   ├── metrics.py                      # Performance monitoring (Optional)
│   │   ├── error_handling.py               # Exception handling patterns (Optional)
│   │   └── config.py                       # Environment configuration
│   ├── api/
│   │   ├── routes/
│   │   │   ├── memory_routes.py            # Memory CRUD API endpoints
│   │   │   ├── voice_routes.py             # Voice processing endpoints
│   │   │   ├── upload_routes.py            # File upload endpoints
│   │   │   └── query_routes.py             # Memory query endpoints
│   │   └── middleware.py                   # Authentication and logging middleware (Skip for now)
│   ├── main.py                             # FastAPI application entry point
│   └── requirements.txt                    # Python dependencies
├── data/
│   ├── memories/
│   │   ├── events.json                     # Episodic memory storage (Can be temporal storage)
│   │   ├── relationships.json              # Person/place relationship graph (Not required for now)
│   │   └── embeddings.json                 # Vector embeddings for search
│   ├── cache/
│   │   └── api_cache.json                  # Cached API responses
│   └── demo/
│       ├── sample_memories.json            # Pre-loaded demo data
│       └── demo_photos/                    # Sample images for demo
├── tests/
│   ├── unit/
│   │   ├── test_agents.py                  # Unit tests for agent classes
│   │   ├── test_orchestrator.py            # Orchestration logic tests
│   │   └── test_services.py                # Service layer tests
│   ├── integration/
│   │   ├── test_api_endpoints.py           # API integration tests
│   │   └── test_agent_coordination.py      # Multi-agent workflow tests
│   └── fixtures/
│       ├── sample_data.py                  # Test data fixtures
│       └── mock_responses.py               # Mock API responses
├── scripts/                                # Optional
│   ├── setup_dev.sh                        # Development environment setup
│   ├── run_demo.sh                         # Demo mode launcher
│   └── deploy.sh                           # Production deployment script
├── .env.example                            # Environment variables template
├── .gitignore                              # Git ignore patterns
├── docker-compose.yml                      # Local development containers
├── README.md                               # Project overview and setup instructions, dependencies and how to run the agent
├── ARCHITECTURE.md                         # System architecture overview (This file)
├── EXPLANATION.md                          # Natural Language Explanation of agent's reasoning, memory, planning, tools and limitations
├── LICENSE                                 # License and policy
└── DEMO.md                                 # Demo instructions and scenarios

## Components

1. **User Interface**  
   - E.g., Streamlit, CLI, Slack bot  

2. **Agent Core**  
   - **Planner**: how you break down tasks  
   - **Executor**: LLM prompt + tool-calling logic  
   - **Memory**: vector store, cache, or on-disk logs  

3. **Tools / APIs**  
   - E.g., Google Gemini API, Tools, etc

4. **Observability**  
   - Logging of each reasoning step  
   - Error handling / retries  

## Architecture Overview
-------------------------
1. Planner Agent (Brain)

   Intent Analysis: Parses voice input to understand user goals
   Task Decomposition: Breaks complex requests into agent-specific tasks
   Agent Selection: Dynamically chooses which agents to activate
   Execution Planning: Determines parallel vs sequential execution patterns

2. Executor Engine (Coordinator)

   Task Queue: Manages parallel/sequential agent execution
   Agent Pool: Maintains agent instances and load balancing
   Result Aggregation: Combines outputs from multiple agents
   Error Handling: Graceful degradation when agents fail

3. Memory Structure (Knowledge Base)

   Event Storage: Structured life event data with rich metadata
   Relationship Graph: Connections between people, places, activities
   Semantic Index: Vector embeddings for intelligent search
   -- Tiered Storage: Hot/Warm/Cold storage for performance optimization

4. Specialized Agents (Workers)

   Voice Agent: Speech-to-text, emotion detection, text-to-speech
   Vision Agent: Photo analysis, object/person recognition
   Context Agent: Gmail/Calendar integration, event correlation
   -- Insight Agent: Pattern detection, relationship analysis 
   Response Agent: Conversational AI, personality, context-aware replies

##  Tool Integrations
Gemini API

   Multimodal Live API: Real-time voice and image processing
   Function Calling: Direct integration with agent methods
   Long Context: Maintains conversation and memory context
   Vision Processing: Advanced photo and document analysis

Google APIs

   Gmail API: Event extraction from emails
   Calendar API: Scheduled event correlation

## Storage & Performance

   JSON Files: Simple, easy to implement persistence
   Vector Embeddings: Semantic search capabilities
   Caching Layer: Performance optimization
   Logging layer: In-memory logs for fault tolerance

Metrics Collection

   Agent response times and success rates
   API usage and rate limiting
   Memory query performance
   -- User interaction patterns

Logging Architecture

   Structured JSON logs with trace IDs
   Request/response payload logging (sanitized)
   -- Error tracking with full context

## Use cases:
1. Conference memory
Feeding to memory:
🎤 YOU: "Hey Life Witness, I just met an amazing person at the conference"

🤖 AGENT: "I'm listening! Tell me about this person while it's fresh in your memory."

🎤 YOU: [Uploads photo of you with a woman at a conference booth] 
       "This is Jennifer Chen, she's a VP of Engineering at Stripe. We talked about 
       their new payment APIs and she mentioned they're hiring senior engineers. 
       She gave me her card and said to reach out about the role."

🤖 AGENT: "I can see you're both at the Stripe booth - that's perfect context! 
         Let me capture this. I notice this is day 2 of the TechCrunch conference 
         based on your calendar. Should I also note that she specifically 
         mentioned hiring for senior engineers?"

🎤 YOU: "Yes, and she said their team is working on crypto payments. Also, 
       she went to Stanford like me - we bonded over that."

🤖 AGENT: "Perfect! I've saved this memory with rich context:
         • Person: Jennifer Chen, VP Engineering at Stripe
         • Connection: Stanford alumni, both interested in crypto
         • Opportunity: Senior engineering role on crypto payments team
         • Action item: Follow up about the position
         • Location: TechCrunch Conference, Stripe booth
         • Relationship strength: Strong initial connection
         
         Should I remind you to follow up with her next week?"

🎤 YOU: "Yes, remind me Tuesday morning."

🤖 AGENT: "Calendar reminder set for Tuesday 9 AM. I'll include her contact details 
         and our conversation context when I remind you."

Query on memory:
🎤 YOU: "Who was that person I met at TechCrunch who worked on crypto payments?"

🤖 AGENT: "That would be Jennifer Chen, VP of Engineering at Stripe! You met her 
         at their booth on day 2 of TechCrunch conference. She mentioned they were 
         hiring senior engineers for their crypto payments team."

🎤 YOU: "Right! What else did we talk about?"

🤖 AGENT: "You both bonded over being Stanford alumni, and she specifically 
         mentioned their new payment APIs. You took a photo together at their booth, 
         and she gave you her business card with instructions to reach out about 
         the senior engineering role."

🎤 YOU: "Did I ever follow up with her?"

🤖 AGENT: "Yes, I reminded you on Tuesday morning as requested, and you sent her 
         a LinkedIn message that same day. She responded within 2 hours suggesting 
         a coffee meeting, which you scheduled for the next Friday. You met at 
         Blue Bottle Coffee downtown and had what you described as a 'great conversation 
         about team culture and technical challenges.'"

🎤 YOU: "Perfect. I'm interviewing at Coinbase tomorrow and want to mention 
       my connection to Stripe's crypto work. Can you give me some talking points?"

🤖 AGENT: "Based on your conversation with Jennifer, here are some relevant points:
         • Stripe is actively investing in crypto infrastructure with dedicated teams
         • They're focusing on enterprise-grade payment solutions (Jennifer's emphasis)
         • Their approach prioritizes regulatory compliance and security
         • Jennifer mentioned they're seeing huge demand from fintech companies
         
         This shows you're plugged into industry trends and have insights from 
         a senior leader in the space. Would you like me to find other crypto-related 
         conversations from your memory?"

      
2. Birthday event memory
Feeding in
🎤 YOU: "Life Witness, I want to remember this moment"

🤖 AGENT: "I'm here! What's happening right now?"

🎤 YOU: [Uploads video of nephew blowing out candles] 
       "It's my nephew Jake's 8th birthday party. He just blew out the candles 
       and made a wish. My sister Sarah organized this whole Minecraft-themed party 
       in their backyard. Jake's been obsessed with Minecraft all year."

🤖 AGENT: "I can see the Minecraft decorations and Jake's huge smile! This looks 
         like such a special moment. I notice your sister really went all out 
         with the theme - there are Minecraft blocks everywhere!"

🎤 YOU: "Yeah, she's amazing at this stuff. Jake was so excited he couldn't 
       even speak when he saw the cake - it was shaped like a Creeper. 
       And all his school friends are here running around in Minecraft costumes."

🤖 AGENT: "That's so sweet! I can hear the joy in your voice. Should I also note 
         that this is at your sister's house in Berkeley? I see from your calendar 
         this party was planned for 2 PM today."

🎤 YOU: "Yes, and I brought him that Lego Minecraft set he's been wanting. 
       His reaction was priceless - he literally jumped up and down. 
       These are the moments I never want to forget."

🤖 AGENT: "I've captured this beautiful memory
         • Event: Jake's 8th birthday party, Minecraft theme
         • Location: Sister Sarah's backyard, Berkeley
         • Key moments: Candle blowing, Creeper cake, costume parade
         • Your gift: Lego Minecraft set - huge success!
         • Emotional context: Pure joy, family connection, pride in sister's effort
         • Attendees: School friends, family
         
         This feels like one of those core family memories. I'll make sure it's 
         easy to find when you want to remember these precious moments with Jake."

Query on:
🎤 YOU: "What did Jake love most about his last birthday party?"

🤖 AGENT: "At Jake's 8th birthday last March, he absolutely loved the Minecraft theme! 
         Your sister Sarah went all out with decorations, and the Creeper-shaped cake 
         was a huge hit. But what really made him light up was the Lego Minecraft set 
         you brought - he literally jumped up and down with excitement."

🎤 YOU: "What else was he into around that time?"

🤖 AGENT: "Based on your memories from that period, Jake was completely obsessed with 
         Minecraft - you mentioned he'd been into it 'all year.' But I also have 
         a memory from two weeks after his party where you took him to the science 
         museum, and he was fascinated by the robotics exhibit. He kept asking 
         how robots are programmed."

🎤 YOU: "Oh right! Has he mentioned robots since then?"

🤖 AGENT: "Yes! In July, you attended his 'invention presentation' at summer camp 
         where he built a simple robot car. You were so proud - you said he 
         explained the programming logic like a little engineer. And just last month 
         at Thanksgiving, he showed everyone a robot he coded to draw patterns."

🎤 YOU: "Wow, I didn't realize he'd gotten so into robotics. What should I get 
       him for his 9th birthday?"

🤖 AGENT: "Based on his evolution from Minecraft to robotics, I'd suggest something 
         that bridges both interests:
         
         • A programmable Minecraft robot kit (combines both passions)
         • Lego Mindstorms (he loved the Lego Minecraft set, now with programming)
         • A beginner Arduino kit with Minecraft-themed projects
         
         Also, remember how much he loved explaining his robot car? He seems to 
         enjoy teaching others, so maybe something he can demonstrate to friends 
         would be perfect. Want me to check what specific robotics projects he's 
         mentioned recently?"

🎤 YOU: "That's brilliant! Can you remind me what Sarah did for decorations last 
       year? I want to help her plan something even better."

🤖 AGENT: "Sarah created an amazing Minecraft wonderland in her Berkeley backyard:
         • Cardboard Minecraft blocks scattered everywhere
         • Creeper-shaped birthday cake (huge hit)
         • All the kids wore Minecraft costumes
         • Green and brown color scheme
         
         For a robotics theme this year, you could suggest:
         • Silver and blue decorations (tech colors)
         • Robot-shaped cake or cupcakes that look like circuit boards
         • A 'robot building station' where kids can assemble simple bots
         • Maybe coordinate with that science museum he loved?
         
         Sarah clearly has amazing party planning skills - she'll probably love 
         collaborating on this evolution from Minecraft to robotics!"