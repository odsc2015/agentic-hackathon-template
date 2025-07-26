# White Mirror Dashboard

A cognitive companion app powered by React (Vite) frontend and FastAPI backend with Google Gemini agents.

---

## Features

- Interactive React dashboard (Vite)
- Cognitive agents (psychologist, mindcoach, facts, etc.)
- FastAPI backend with Gemini LLM integration
- Parallel agent workflow and session management

---

## Getting Started

### 1. **Frontend (React + Vite)**

```bash
cd white-mirror-dashboard
npm install
npm run dev
```
Visit [http://localhost:5173](http://localhost:5173) in your browser.

---

### 2. **Backend (FastAPI + Gemini)**

```bash
cd ../src
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API runs at [http://localhost:8000](http://localhost:8000).

---

### 3. **Environment Variables**

Create a `.env` file in your backend folder with:

```
GEMINI_API_KEY=your_google_gemini_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
```

---

## Project Structure

```
white-mirror-dashboard/   # React frontend
src/                      # FastAPI backend
  agents/                 # Cognitive agent modules
  main.py                 # FastAPI entrypoint
  workflow.py             # Parallel agent workflow
  Planner.py              # Gemini planner logic
```

---

## Usage

- Start backend and frontend servers.
- Interact with cognitive agents via the dashboard.
- Each chat/query creates a fresh session and agent workflow.

---

## License

MIT
