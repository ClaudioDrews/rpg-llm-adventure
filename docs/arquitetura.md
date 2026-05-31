# RPG LLM Adventure — Documentação Técnica

**Data:** 2026-05-30
**Versão do projeto:** 1.0
**Local:** `rpg-llm-adventure/` (raiz do projeto)

---

## 1. Visão Geral

Jogo de RPG por texto no estilo **Fighting Fantasy** (Aventuras Fantásticas), onde um LLM atua como mestre de jogo, gerando narrativa interativa com 3 opções de ação por rodada.

**Diferencial:** suporte a múltiplos provedores de LLM, interface web responsiva (PC + celular), e logs completos das aventuras.

---

## 2. Arquitetura

```
┌──────────────┐     HTTP/API      ┌──────────────┐     HTTP/LLM API     ┌─────────────┐
│   Frontend   │ ◄──────────────► │   Backend    │ ◄──────────────────► │  Provedor   │
│  (vanilla JS)│                   │  (FastAPI)   │                       │  de LLM     │
│              │                   │              │                       │             │
│ index.html   │                   │ main.py      │                       │ Ollama      │
│ app.js       │                   │ llm_manager  │                       │ OpenAI      │
│              │                   │ game_state   │                       │ Anthropic   │
└──────────────┘                   └──────────────┘                       └─────────────┘
     Porta 8000
     Acesso local + rede
```

### Fluxo de comunicação

1. Frontend faz `POST /api/game/start` com configuração da aventura
2. Backend monta prompt para o LLM, gera introdução com 3 opções
3. Jogador envia `POST /api/game/action` com escolha (1, 2, 3 ou texto)
4. Backend alimenta LLM com histórico + ação, gera próxima rodada
5. Na rodada 20, backend gera conclusão épica e arquivo de log

---

## 3. Componentes

### 3.1 Backend (`backend/`)

| Arquivo | Função |
|---------|--------|
| `main.py` | Servidor FastAPI, rotas, parsing de resposta LLM, geração de logs |
| `llm_manager.py` | Abstração de provedores LLM (Ollama, OpenAI, Anthropic) |
| `game_state.py` | Dataclasses: `GameConfig` e `GameState` (histórico de rodadas) |

#### Rotas da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Serve `frontend/index.html` |
| `POST` | `/api/game/start` | Inicia nova aventura |
| `POST` | `/api/game/action` | Processa ação do jogador |
| `GET` | `/api/logs/{filename}` | Download do log da aventura |

#### LLMManager (provedores)

| Provedor | Endpoint | Timeout |
|----------|----------|---------|
| Ollama | `POST /api/generate` (localhost:11434) | 120s |
| OpenAI | `POST /api.openai.com/v1/chat/completions` | 60s |
| Anthropic | `POST /api.anthropic.com/v1/messages` | 60s |

### 3.2 Frontend (`frontend/`)

- `index.html` — Interface completa com design terminal CRT
- `app.js` — Lógica: fetch para API, renderização, handlers de teclado

### 3.3 CLI (`cli/rpg_cli.py`)

Interface de terminal com setup interativo, loop de jogo, e salvamento de log.

---

## 4. Dependências

| Pacote | Versão | Uso |
|--------|--------|-----|
| fastapi | 0.115.0 | Framework web |
| uvicorn[standard] | 0.32.0 | Servidor ASGI |
| pydantic | 2.9.2 | Validação de dados |
| httpx | 0.27.2 | Cliente HTTP async |
| python-multipart | 0.0.12 | Suporte a form data |

---

## 5. Estado atual

### Funcionalidades
- ✅ CRUD de aventuras (start → ação × 19 → conclusão)
- ✅ 3 provedores de LLM
- ✅ Interface web responsiva + CLI
- ✅ Ações customizadas
- ✅ Logs com download
- ✅ Script `start.sh` funcional

### Pendente
- ❌ Persistência de sessões
- ❌ WebSocket para streaming
- ❌ Sistema de personagem (atributos, inventário)
- ❌ Salvamento parcial

---

## 6. Convenções

- **Idioma:** docstrings em português; código em inglês
- **Tipagem:** type hints em todas as assinaturas
- **Async:** FastAPI com `async/await`
- **Nomenclatura:** PascalCase classes, snake_case funções
