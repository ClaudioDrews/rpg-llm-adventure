# 🎲 RPG LLM ADVENTURE - VISÃO GERAL DO PROJETO

## 📊 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Usuário)                         │
│  ┌──────────────┐              ┌──────────────┐             │
│  │   Terminal   │              │  Navegador   │             │
│  │   (CLI)      │              │  (Web/Mobile)│             │
│  └──────┬───────┘              └──────┬───────┘             │
└─────────┼──────────────────────────────┼───────────────────┘
          │                              │
          │                              │ HTTP
          │                              │
┌─────────▼──────────────────────────────▼───────────────────┐
│               SERVIDOR BACKEND (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  main.py - API REST Endpoints                        │  │
│  │  • /api/game/start    - Iniciar aventura             │  │
│  │  • /api/game/action   - Processar ação               │  │
│  │  • /api/logs/{file}   - Download de logs             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  llm_manager.py - Gerenciador de LLMs                │  │
│  │  • Ollama (Local)                                    │  │
│  │  • OpenAI API                                        │  │
│  │  • Anthropic API                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  game_state.py - Gerenciamento de Estado             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────┬──────────────────────────────┬───────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────┐          ┌─────────────────────┐
│  Ollama Local   │          │   APIs Externas     │
│  (llama3.2)     │          │  • OpenAI           │
│                 │          │  • Anthropic        │
└─────────────────┘          └─────────────────────┘
```

## 🔄 Fluxo de Jogo

```
┌─────────────────┐
│   1. SETUP      │  Usuário configura tipo de LLM, estilo, época, contexto
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. INTRODUÇÃO   │  LLM gera narrativa inicial + 3 opções de ação
│   (Rodada 1)    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. LOOP JOGO    │  Rodadas 2-19: usuário age → LLM continua história
│ (Rodadas 2-19)  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  4. FINAL       │  Rodada 20: LLM gera conclusão épica, sem opções
│   (Rodada 20)   │
└────────┬────────┘
         ▼
┌─────────────────┐
│  5. LOG FINAL   │  Sistema salva aventura_XXXXX.txt com histórico completo
└─────────────────┘
```

## 📁 Estrutura de Arquivos

```
rpg-llm-adventure/
├── 📄 README.md
├── 📄 QUICKSTART.md
├── 📄 requirements.txt
├── 🔧 start.sh
├── 📄 .gitignore
├── 📂 backend/
│   ├── main.py
│   ├── llm_manager.py
│   └── game_state.py
├── 📂 frontend/
│   ├── index.html
│   └── app.js
├── 📂 cli/
│   └── rpg_cli.py
└── 📂 logs/          (auto-criado)
    └── aventura_*.txt
```

## 🎨 Design da Interface

- **Inspiração**: Terminal CRT vintage
- **Paleta**: Preto (#000) + Verde terminal (#33ff33)
- **Tipografia**: VT323 (monospace retro)
- **Efeitos**: Scanlines, flicker, glow, cursor piscante

## 🔒 Segurança

- API keys nunca são logadas
- Validação de entrada com Pydantic
- Timeout em requisições HTTP
- Sanitização de inputs do usuário

## 🚀 Roadmap Futuro

- [ ] Sistema de salvamento (salvar/carregar partida)
- [ ] Sistema de inventário e atributos
- [ ] Modo multiplayer
- [ ] Geração de imagens
- [ ] Narração por áudio (TTS)
- [ ] Docker/Docker Compose
- [ ] Testes automatizados

---

**Criado com 💜 para entusiastas de RPG e IA**

*Boa aventura, desenvolvedor!* ⚔️🐉✨
