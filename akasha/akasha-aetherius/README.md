# akasha-aetherius

**Celestial GitHub issue management engine — Akasha Constellation**

Aetherius scans GitHub repositories, ranks open issues by priority, generates
code stubs via a pluggable LLM interface, and records every action in an
append-only **Aetherius Ledger**. A sliding-window **Governor** enforces safe
API rate limits. Human stewards approve all writes and priority adjustments
through a live React dashboard.

---

## Akasha Position

```
Layer  : management
Role   : engine
Status : canonical
```

Aetherius aligns with all 10 Akasha axioms. See `AKASHA_ALIGNMENT.md`.

---

## Features

- **Live GitHub Issue Scanning** — polls declared repos on a configurable interval
- **Priority Ranking** — heuristic scorer with label awareness (bug / critical / urgent)
- **LLM Code Generation** — pluggable stub; wire to any model endpoint
- **Human Feedback** — adjust issue priority scores in real-time via dashboard
- **Sliding-Window Governor** — enforces GitHub and LLM call limits per minute
- **Aetherius Ledger** — append-only audit trail, every action recorded
- **Live Dashboard** — React + Tailwind + SocketIO; issue cards, code editor, ledger view
- **GitHub File Push** — write generated patches directly to repos from the dashboard

---

## Directory Layout

```
akasha-aetherius/
├── backend/
│   ├── aetherius_governor.py   # rate limiter
│   ├── aetherius_engine.py     # scan / rank / generate / feedback
│   └── aetherius_backend.py    # Flask + SocketIO server
├── frontend/
│   ├── src/
│   │   ├── AetheriusDashboard.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── tests/
│   └── test_smoke.py
├── docs/                        (reserved)
├── schemas/                     (reserved)
├── install-debian.sh
├── pyproject.toml
├── repo-manifest.yaml
├── AKASHA_ALIGNMENT.md
├── CONSTELLATION_ENTRY.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## Installation — Debian 13

```bash
# One-shot bootstrap (requires sudo for apt)
chmod +x install-debian.sh
./install-debian.sh
```

Or manually:

```bash
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[prod]"
cd frontend && npm install && cd ..
```

---

## Configuration

All secrets and tunables are environment variables — **never hardcode tokens**.

| Variable | Default | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | *(required)* | GitHub personal access token |
| `AETHERIUS_REPOS` | `yourusername/repo1` | Comma-separated `owner/repo` list |
| `AETHERIUS_HOST` | `0.0.0.0` | Backend bind host |
| `AETHERIUS_PORT` | `5000` | Backend bind port |
| `AETHERIUS_SCAN_INTERVAL` | `60` | Seconds between issue scans |
| `AETHERIUS_SECRET` | `aetherius-dev-secret` | Flask session secret |

---

## Running

**Terminal 1 — backend:**
```bash
source .venv/bin/activate
export GITHUB_TOKEN="ghp_your_token_here"
export AETHERIUS_REPOS="owner/repo1,owner/repo2"
python backend/aetherius_backend.py
```

**Terminal 2 — dashboard:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:3000**

---

## API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/issues` | Ranked issue list |
| GET | `/api/ledger` | Audit trail |
| GET | `/api/governor` | Current rate-limit status |
| POST | `/api/governor` | Update rate limits |
| POST | `/api/feedback` | Adjust issue priority |
| POST | `/api/update_file` | Push file to GitHub |
| GET | `/api/health` | Health check |

**WebSocket:** connect to `http://localhost:5000` — receives `update` events
with `{ issues, ledger }` on every scan cycle or human action.

---

## Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

9 smoke tests covering governor throttling, engine scoring, feedback,
and ledger tracing.

---

## Wiring a Real LLM

In `backend/aetherius_engine.py`, replace the body of `generate_llm_code()`
with your preferred API call. The governor check and ledger entry are already
in place. Example for Anthropic:

```python
import anthropic
client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Write Python code for: {prompt}"}]
)
return msg.content[0].text
```

---

## License

MIT License — Copyright (c) 2025 TheGreatOleander

---

## Akasha

This repository participates in the Akasha ecosystem and is described by
`repo-manifest.yaml`. It aligns with `akasha-axioms`, `akasha-world`,
and `akasha-constellation`.
