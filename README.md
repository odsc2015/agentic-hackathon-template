# 🧠 White Mirror Dashboard

> A cognitive wellness platform that transforms mental health support through AI-powered personalized guidance and real-time brain activity visualization (Well thats the Aim)
> ## 🌟 Vision

White Mirror is the opposite of Black Mirror - using technology to enhance human wellbeing rather than exploit it. Our platform combines cutting-edge AI agents with interactive brain visualization to create a personalized cognitive companion that helps users:

- **Understand** their mental patterns through real-time brain activity visualization
- **Improve** cognitive abilities with personalized training exercises
- **Heal** through AI-guided therapeutic conversations
- **Learn** with adaptive educational pathways tailored to their brain's unique patterns

<img width="3280" height="1856" alt="image" src="https://github.com/user-attachments/assets/44e34e8c-1de1-4783-a0d8-a46b93951c72" />


## 🎯 Core Features

### 🤖 Cognitive AI Agents
- **Psychologist Agent**: Provides evidence-based therapeutic support and coping strategies
- **Mind Coach Agent**: Develops personalized brain training exercises and tracks progress
- **Wellness Agent**: Monitors overall mental health and suggests lifestyle improvements
- **Learning Agent**: Creates adaptive learning paths based on cognitive strengths
- **Facts Agent**: Provides scientifically-backed information about brain health

### 🧬 Brain Visualization
- **3D Brain Model**: Interactive visualization that responds to user's cognitive state
- **Real-time Activity**: Neural pathways light up based on current mental engagement
- **Progress Tracking**: Visual representation of cognitive improvements over time

### 📊 Personalized Dashboard
- **Session Management**: Track therapy sessions, exercises, and learning progress
- **Analytics**: Detailed insights into cognitive patterns and improvements
- **Goal Setting**: Create and monitor personal development objectives
- **Resource Library**: Curated content based on individual needs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (React)                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 3D Brain    │  │ Chat         │  │ Analytics        │  │
│  │ Visualizer  │  │ Interface    │  │ Dashboard        │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ WebSocket/REST API
┌─────────────────────────┴───────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Session     │  │ Agent        │  │ Workflow         │  │
│  │ Manager     │  │ Orchestrator │  │ Engine           │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                   Google Gemini LLM                          │
│         Parallel Processing of Multiple Agents               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Google Gemini API key

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/white-mirror-dashboard.git
cd white-mirror-dashboard
```

### 2. Frontend Setup (React + Vite)
```bash
cd white-mirror-dashboard
npm install
npm run dev
```
The frontend will be available at [http://localhost:5173](http://localhost:5173)

### 3. Backend Setup (FastAPI + Gemini)
```bash
cd ../src
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `src` directory:
```env
# Google Gemini Configuration
GEMINI_API_KEY=your_google_gemini_api_key
GOOGLE_API_KEY=your_google_gemini_api_key

# Application Settings
DEBUG=True
SESSION_SECRET_KEY=your_secret_key_here
CORS_ORIGINS=["http://localhost:5173"]

# Database (Future Implementation)
DATABASE_URL=sqlite:///./white_mirror.db
```

### 5. Start the Backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
API documentation available at [http://localhost:8000/docs](http://localhost:8000/docs)

## 📁 Project Structure

```
white-mirror/
├── white-mirror-dashboard/      # React Frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── BrainVisualizer/
│   │   │   ├── ChatInterface/
│   │   │   └── Dashboard/
│   │   ├── pages/             # Main application pages
│   │   ├── services/          # API integration
│   │   └── store/             # State management
│   └── package.json
│
├── src/                       # FastAPI Backend
│   ├── agents/               # Cognitive agent modules
│   │   ├── psychologist.py
│   │   ├── mindcoach.py
│   │   ├── wellness.py
│   │   ├── learning.py
│   │   └── facts.py
│   ├── core/                # Core functionality
│   │   ├── session.py      # Session management
│   │   ├── workflow.py     # Agent orchestration
│   │   └── config.py       # Configuration
│   ├── api/                # API endpoints
│   │   ├── chat.py
│   │   ├── analytics.py
│   │   └── sessions.py
│   ├── models/             # Data models
│   ├── main.py            # FastAPI entry point
│   └── requirements.txt
│
└── docs/                   # Documentation
    ├── API.md
    ├── AGENTS.md
    └── DEPLOYMENT.md
```

## 🔧 Technical Details

### Frontend Technologies
- **React 18** with TypeScript
- **Vite** for fast development
- **Three.js** for 3D brain visualization
- **Socket.io** for real-time updates
- **Material-UI** for consistent design
- **Zustand** for state management

### Backend Technologies
- **FastAPI** for high-performance API
- **Google Gemini** for AI capabilities
- **Pydantic** for data validation
- **SQLAlchemy** for future database integration
- **Redis** for session management (planned)

### AI Agent System
Each agent is designed with specific expertise:
- Parallel processing for faster responses
- Context-aware conversations
- Session persistence across interactions
- Personalized recommendations based on user patterns

## 🎮 Usage Guide

1. **First Visit**: Complete a brief cognitive assessment
2. **Dashboard**: View your personalized brain visualization
3. **Chat**: Interact with different AI agents based on your needs
4. **Exercises**: Complete daily brain training activities
5. **Track Progress**: Monitor improvements in various cognitive areas

## 🐛 Known Issues & Roadmap

### Current Limitations
- Session persistence needs improvement
- WebSocket connections occasionally drop
- Brain visualization performance on mobile devices

### Upcoming Features
- [ ] Mobile app version
- [ ] Offline mode with local AI models
- [ ] Integration with wearable devices
- [ ] Multi-language support
- [ ] Voice interaction capabilities
- [ ] Collaborative sessions with therapists

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Run tests
npm test          # Frontend
pytest            # Backend

# Code formatting
npm run format    # Frontend
black .           # Backend
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini team for the powerful LLM
- React Three Fiber community for 3D visualization tools
- FastAPI contributors for the excellent framework
- Our early testers for valuable feedback

## 📞 Contact

- **Project Lead**: [Your Name]
- **Email**: your.email@example.com
- **Discord**: [Join our community](https://discord.gg/your-invite)
- **Twitter**: [@WhiteMirrorAI](https://twitter.com/WhiteMirrorAI)

---

<p align="center">
  Made with ❤️ for mental wellness
</p>
