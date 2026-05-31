#!/usr/bin/env python3
"""
RPG Text Adventure - Backend Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List, Literal
import uvicorn
import json
import subprocess
from datetime import datetime
from pathlib import Path
import socket

from llm_manager import LLMManager
from game_state import GameState, GameConfig


def get_local_ip():
    try:
        result = subprocess.run(["ip", "route", "get", "1"], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            parts = result.stdout.split()
            for i, part in enumerate(parts):
                if part == "src" and i + 1 < len(parts):
                    ip = parts[i + 1]
                    if not ip.startswith("127."):
                        return ip
    except:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith("127."):
            return ip
    except:
        pass
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if not ip.startswith("127."):
            return ip
    except:
        pass
    return "localhost"

app = FastAPI(title="RPG LLM Adventure")
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
llm_manager = LLMManager()
active_games = {}


class GameSetup(BaseModel):
    llm_type: Literal["ollama", "openai", "anthropic"]
    llm_model: str = "llama3.2"
    api_key: Optional[str] = None
    narrative_style: str = "épico e descritivo"
    era: str = "fantasia medieval"
    context: str = "reino em guerra"
    protagonist: str = "um jovem aventureiro"
    characters: str = "magos, guerreiros e criaturas místicas"


class PlayerAction(BaseModel):
    session_id: str
    action: str


class GameResponse(BaseModel):
    session_id: str
    round: int
    narrative: str
    options: List[str]
    is_final: bool = False
    log_file: Optional[str] = None


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.post("/api/game/start")
async def start_game(setup: GameSetup) -> GameResponse:
    try:
        config = GameConfig(llm_type=setup.llm_type, llm_model=setup.llm_model, api_key=setup.api_key, narrative_style=setup.narrative_style, era=setup.era, context=setup.context, protagonist=setup.protagonist, characters=setup.characters)
        llm_manager.configure(llm_type=setup.llm_type, model=setup.llm_model, api_key=setup.api_key)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        game_state = GameState(config=config, session_id=session_id)
        active_games[session_id] = game_state
        intro_prompt = f"""Você é um mestre de RPG criando uma aventura no estilo dos livros "Aventuras Fantásticas" (Fighting Fantasy).

CONFIGURAÇÃO DA AVENTURA:
- Estilo narrativo: {config.narrative_style}
- Época: {config.era}
- Contexto: {config.context}
- Protagonista: {config.protagonist}
- Personagens: {config.characters}

Crie a INTRODUÇÃO da aventura (Rodada 1 de 20):
1. Escreva uma introdução envolvente e imersiva (2-3 parágrafos)
2. Descreva a situação inicial do protagonista
3. Apresente EXATAMENTE 3 opções de ação claras e interessantes

Formato de resposta:
[NARRATIVA]
(texto da introdução)

[OPÇÕES]
1. (primeira opção)
2. (segunda opção)
3. (terceira opção)"""
        response = await llm_manager.generate(intro_prompt)
        narrative, options = _parse_llm_response(response)
        game_state.add_round(narrative, options, None)
        return GameResponse(session_id=session_id, round=1, narrative=narrative, options=options, is_final=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar jogo: {str(e)}")


@app.post("/api/game/action")
async def process_action(action: PlayerAction) -> GameResponse:
    try:
        if action.session_id not in active_games:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        game_state = active_games[action.session_id]
        if game_state.current_round >= 20:
            raise HTTPException(status_code=400, detail="Jogo já finalizado")
        last_round = game_state.rounds[-1]
        if action.action in ["1", "2", "3"]:
            chosen_action = last_round["options"][int(action.action) - 1]
        else:
            chosen_action = action.action
        game_state.rounds[-1]["player_action"] = chosen_action
        next_round = game_state.current_round + 1
        is_final = (next_round == 20)
        if is_final:
            continuation_prompt = f"""Continue a aventura de RPG (estilo Fighting Fantasy).

RODADA FINAL (20/20) - CONCLUSÃO DA HISTÓRIA

Contexto da história:
{_format_history(game_state.rounds[-3:])}

Última ação do jogador: {chosen_action}

Crie a CONCLUSÃO ÉPICA da aventura:
1. Resolva a ação do jogador de forma dramática
2. Conclua todos os arcos narrativos principais
3. Descreva o desfecho da história
4. Dê um fechamento satisfatório para o protagonista
5. NÃO apresente mais opções

Formato de resposta:
[NARRATIVA]
(texto conclusivo - 3-4 parágrafos)

[FIM DA AVENTURA]"""
        else:
            continuation_prompt = f"""Continue a aventura de RPG (estilo Fighting Fantasy).

RODADA {next_round}/20

Contexto recente:
{_format_history(game_state.rounds[-2:])}

Última ação do jogador: {chosen_action}

Continue a história:
1. Descreva o resultado da ação do jogador
2. Desenvolva a narrativa (2-3 parágrafos)
3. Apresente EXATAMENTE 3 novas opções de ação

Formato de resposta:
[NARRATIVA]
(texto da continuação)

[OPÇÕES]
1. (primeira opção)
2. (segunda opção)
3. (terceira opção)"""
        response = await llm_manager.generate(continuation_prompt)
        if is_final:
            narrative = response.split("[NARRATIVA]")[-1].split("[FIM")[0].strip()
            options = []
        else:
            narrative, options = _parse_llm_response(response)
        game_state.add_round(narrative, options, chosen_action)
        log_file = None
        if is_final:
            log_file = _generate_log_file(game_state)
        return GameResponse(session_id=action.session_id, round=next_round, narrative=narrative, options=options, is_final=is_final, log_file=log_file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar ação: {str(e)}")


@app.get("/api/logs/{filename}")
async def download_log(filename: str):
    file_path = LOGS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(file_path, filename=filename)


@app.get("/app.js")
async def serve_js():
    return FileResponse(str(FRONTEND_DIR / "app.js"))


@app.get("/favicon.ico")
async def favicon():
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#000"/><text x="4" y="24" font-family="monospace" font-size="20" fill="#33ff33" font-weight="bold">&gt;_</text></svg>'
    return Response(content=svg_content, media_type="image/svg+xml")


def _parse_llm_response(response: str) -> tuple:
    try:
        parts = response.split("[OPÇÕES]")
        narrative = parts[0].replace("[NARRATIVA]", "").strip()
        options_text = parts[1].strip()
        options = []
        for line in options_text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                option = line.split(".", 1)[-1].strip()
                if option:
                    options.append(option)
        return narrative, options[:3]
    except:
        return response, ["Investigar mais a fundo", "Seguir em frente com cautela", "Tentar uma abordagem diferente"]


def _format_history(rounds: List[dict]) -> str:
    """Format round history for LLM context."""
    history = []
    for r in rounds:
        history.append(f"Narrativa: {_smart_truncate(r['narrative'], 200)}...")
        if r['player_action']:
            history.append(f"Ação do jogador: {r['player_action']}")
    return "\n".join(history)


def _smart_truncate(text: str, max_chars: int) -> str:
    """Truncate text at a word boundary, preserving whole words."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars // 2:
        return text[:last_space]
    return truncated


def _generate_log_file(game_state: GameState) -> str:
    filename = f"aventura_{game_state.session_id}.txt"
    filepath = LOGS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("AVENTURA FANTÁSTICA - LOG COMPLETO\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Sessão: {game_state.session_id}\n\n")
        f.write("CONFIGURAÇÃO DA AVENTURA:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Estilo Narrativo: {game_state.config.narrative_style}\n")
        f.write(f"Época: {game_state.config.era}\n")
        f.write(f"Contexto: {game_state.config.context}\n")
        f.write(f"Protagonista: {game_state.config.protagonist}\n")
        f.write(f"Personagens: {game_state.config.characters}\n")
        f.write(f"LLM: {game_state.config.llm_type} ({game_state.config.llm_model})\n\n")
        f.write("=" * 80 + "\n")
        f.write("A AVENTURA\n")
        f.write("=" * 80 + "\n\n")
        for i, round_data in enumerate(game_state.rounds, 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"RODADA {i}/20\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(round_data['narrative'])
            f.write("\n\n")
            if round_data['options']:
                f.write("OPÇÕES APRESENTADAS:\n")
                for j, option in enumerate(round_data['options'], 1):
                    f.write(f"{j}. {option}\n")
                f.write("\n")
            if round_data['player_action']:
                f.write(f">>> AÇÃO DO JOGADOR: {round_data['player_action']}\n")
        f.write("\n" + "=" * 80 + "\n")
        f.write("FIM DA AVENTURA\n")
        f.write("=" * 80 + "\n")
    return filename


if __name__ == "__main__":
    local_ip = get_local_ip()
    print("\n" + "=" * 60)
    print("🎲 RPG LLM ADVENTURE - Servidor Iniciado")
    print("=" * 60)
    print(f"\n📱 Acesso Local: http://localhost:8000")
    print(f"🌐 Acesso na Rede: http://{local_ip}:8000")
    print(f"\n💡 Para acessar do celular:")
    print(f"   1. Conecte o celular na mesma rede WiFi")
    print(f"   2. Abra o navegador e acesse: http://{local_ip}:8000")
    print("\n" + "=" * 60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
