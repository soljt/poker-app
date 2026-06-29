# Poker App

A full-stack, real-time multiplayer Texas Hold'em poker game built from scratch. Multiple players can join a shared lobby, create or join live games, and play against each other (or against bots) with chips that persist across sessions.

**Live at [poker.soljt.ch](https://poker.soljt.ch)**

---

## Features

**Gameplay**
- Full Texas Hold'em rules: preflop, flop, turn, and river with side pots, all-ins, and showdowns
- Real-time updates pushed to every player via WebSocket so the table state is always in sync
- Per-player game state serialization: each player only sees their own hole cards, never anyone else's
- Inaction timer that auto-folds a player after 45 seconds and kicks them from the game
- Rebuy system that offers broke players a chance to top up their stack before the next hand starts
- Mid-game join queue so new players can be seated without interrupting the current hand

**Bots**
- Pluggable bot architecture: any `DecisionEngine` implementation can be dropped in without touching the game loop
- Heuristic engine that scores hands using a weighted blend of current made-hand strength and draw potential, factoring in pot odds, kicker quality, and preflop bonuses (suited connectors, pocket pairs)
- Gemini LLM engine that sends the full game state to the Gemini API and parses a structured JSON action response, with a fallback to a random engine if the API call fails

**Auth and Security**
- JWT stored in httpOnly cookies with CSRF token verification on state-changing requests
- Rate limiting on auth endpoints backed by Redis in production
- Role-based access control: admin users can manage accounts, regular users cannot access admin routes

**Admin Panel**
- Paginated user management table with create, edit, and delete actions
- Chip balance adjustment and role management with guard rails (admins cannot be promoted or demoted by non-admins)

**Infrastructure**
- Containerized with Docker Compose: Flask/Gunicorn backend, Nginx-served React frontend, PostgreSQL, and Redis
- Images published to GitHub Container Registry and pulled at deploy time
- All traffic routed through a central Nginx reverse proxy on the host VM
- Game hand data written to append-only JSONL files (one file per day) with full action history, board state, and hole cards per action

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, React Bootstrap, Socket.IO client, React Router |
| Backend | Python, Flask, Flask-SocketIO, Gunicorn + eventlet |
| Auth | Flask-JWT-Extended (httpOnly cookies + CSRF) |
| Database | PostgreSQL (production), SQLite (development), SQLAlchemy ORM |
| Caching / Rate limiting | Redis, Flask-Limiter, Flask-Caching |
| AI Bots | Google Gemini API (`gemini-2.0-flash`) |
| Infrastructure | Docker, Docker Compose, Nginx, GitHub Container Registry |

---

## Architecture

The browser talks to a central Nginx reverse proxy, which routes requests to the appropriate container. REST calls (auth, game state queries, leaderboard) go through axios. Real-time game events and player actions go through Socket.IO over WebSocket.

```
Browser
  |
  v
Central Nginx (reverse proxy, host VM)
  |
  +-- /           --> Frontend container (Nginx, serves built React app)
  +-- /api/*      --> Backend container (Flask via Gunicorn/eventlet)
  +-- /socket.io  --> Backend container (Socket.IO)
                         |
                         +-- PostgreSQL (user + chip data)
                         +-- Redis (rate limiting, caching)
```

Active game state (players, bets, deck, timers) lives in memory on the backend. The database only stores user accounts and chip balances, which are written at the end of each hand.

---

## Getting Started

**Prerequisites:** Docker and Docker Compose.

### With Docker (recommended)

```bash
# Copy the example env file and fill in your secrets
cp .env.example .env

docker-compose up -d
```

The app will be available at `http://localhost`.

### Without Docker (local development)

**Backend**

```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python run.py
# Runs on http://localhost:5000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

By default the frontend dev server points to `http://localhost:5000` for API calls (set in `frontend/.env.development`).

---

## Running Tests

```bash
cd backend
pytest -v
```

Tests cover the hand evaluation engine: card ranking, hand comparison, tie-breaking, side pot calculation, and edge cases like ace-low straights.

---

## Project Structure

```
poker-app/
├── backend/
│   ├── app/
│   │   ├── auth/          # Login, register, JWT handling
│   │   ├── admin/         # Admin-only user management routes
│   │   ├── bot/           # Bot framework: decision engines, heuristic, Gemini
│   │   ├── game_logic/    # Core poker engine (Card, Deck, Hand, PokerRound)
│   │   ├── recording/     # JSONL game hand recorder
│   │   ├── sockets/       # Socket.IO event handlers and game flow
│   │   ├── models/        # SQLAlchemy models (User)
│   │   └── globals.py     # In-memory game state
│   └── run.py
└── frontend/
    └── src/
        ├── views/         # Page components (Game, Lobby, Landing, Admin, Leaderboard)
        ├── components/    # Shared UI components
        ├── context/       # useAuth, useSocket React contexts
        └── services/      # axios instance
```
