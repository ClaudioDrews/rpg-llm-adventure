# 🎲 RPG LLM Adventure

**AI-powered Fighting Fantasy adventures — now bilingual, local-first, and open-source.**

A text-based RPG inspired by the classic *Fighting Fantasy* gamebooks by Ian Livingstone and Steve Jackson. You configure a world, choose your AI narrator, and live a unique adventure generated in real time. No two playthroughs are ever the same.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🤖 **Multiple backends** — Ollama (local), OpenAI, Anthropic. Mix and match.
- 🌐 **Bilingual** — Portuguese and English UI, with browser language detection.
- 📱 **Responsive** — Play on desktop or phone. Same WiFi = instant access.
- 🎨 **Two themes** — CRT terminal (green-on-black) or Book Mode (parchment).
- ⚙️ **Configurable** — Rounds (8/12/20/unlimited), temperature, max tokens, narrative style.
- 📝 **Markdown logs** — Every adventure saved with YAML frontmatter. Readable anywhere.
- ⌨️ **Keyboard shortcuts** — Press `1`, `2`, `3` to choose. Custom actions for anything else.
- 🔒 **Local-first** — Ollama mode needs no internet, no account, no API key.

---

## 📋 Requirements

- Python 3.10+
- Ollama (optional, for local/free mode)

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/ClaudioDrews/rpg-llm-adventure.git
cd rpg-llm-adventure

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start (with Ollama)
ollama serve &
ollama pull llama3.2

# Run
cd backend && python main.py
# → Open http://localhost:8000
```

---

## 🎮 How to Play

### Web Interface

1. Start the server: `cd backend && python main.py`
2. Open `http://localhost:8000` (or the network IP shown in the console)
3. Configure your world — era, context, protagonist, characters
4. Click **Start Adventure** and begin your journey

### During the game

- **1/2/3 keys** — Choose one of three pre-generated options
- **Custom input** — Type any action you can imagine
- **Full History** — Expand the accordion to see all past rounds
- **End Adventure** — Conclude the story at any round
- **Theme toggle** — Switch between Terminal and Book mode in the top-right corner

### Mobile

Connect your phone to the same WiFi as the server. Open the IP shown in the console (e.g. `http://192.168.8.30:8000`). The interface is fully responsive.

---

## 📂 Project Structure

```
rpg-llm-adventure/
├── backend/
│   ├── main.py          # FastAPI server + all endpoints
│   ├── llm_manager.py   # LLM provider abstraction
│   └── game_state.py    # Game state data model
├── frontend/
│   ├── index.html       # Full UI (HTML + CSS)
│   └── app.js           # Frontend logic (vanilla JS)
├── cli/
│   └── rpg_cli.py       # Terminal interface
├── logs/                # Adventure logs (Markdown + YAML frontmatter)
├── requirements.txt
├── start.sh
└── CHANGELOG.md
```

---

## ⚙️ Configuration

### Provider Setup

Use the **Options** menu on the start screen to select your LLM provider and model. The "Load Models" button discovers available Ollama models automatically.

### Adventure Parameters

- **Narrative Style** — epic, humorous, dark, romantic...
- **Era** — medieval fantasy, cyberpunk, post-apocalyptic, space exploration...
- **Duration** — 8, 12, 20 rounds, or "Until the end" (no limit)
- **Advanced** — temperature (creativity) and max tokens (response length)

---

## 🐛 Troubleshooting

### "Could not connect to Ollama"

```bash
ollama serve                    # Start the service
ollama list                     # Verify models are available
```

### "Port 8000 already in use"

```bash
sudo lsof -ti:8000 | xargs kill -9
```

### Mobile can't connect

1. Confirm phone and server are on the same WiFi
2. Use the IP shown in the console (not `localhost`)
3. Temporarily disable firewall if blocked

---

## 🤝 Contributing

Bug reports, feature suggestions, and pull requests are welcome.

Areas where you can help:
- **New LLM providers** — add a `_generate_<provider>()` method to `llm_manager.py`
- **Visual themes** — add CSS classes for new color schemes
- **Translations** — add entries to the `I18N` dictionary in `app.js`

---

## 📄 License

MIT — use, modify, and distribute freely.

---

*"Sua decisão pode mudar tudo." — "Your decision can change everything."*
