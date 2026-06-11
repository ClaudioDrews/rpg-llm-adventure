#!/usr/bin/env python3
"""
RPG Text Adventure - Backend Server
Sistema de RPG por texto alimentado por LLM
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List, Literal
import uvicorn
import json
import os
import subprocess
from datetime import datetime
import uuid
from pathlib import Path
import socket
import re
import httpx

# Importar módulos do projeto
from llm_manager import LLMManager
from game_state import GameState, GameConfig
from utils.text_parsers import parse_llm_response, format_history
from services.log_service import generate_log_file
from services.game_store import GameStore


def get_local_ip():
    try:
        result = subprocess.run(
            ["ip", "route", "get", "1"],
            capture_output=True,
            text=True,
            timeout=2
        )
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

@app.on_event("startup")
async def startup():
    await game_store.start_cleanup()

@app.on_event("shutdown")
async def shutdown():
    await game_store.stop_cleanup()

# Configurações
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configurar diretório do frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

game_store = GameStore(ttl_seconds=3600)

# Models
class GameSetup(BaseModel):
    llm_type: Literal["ollama", "openai", "anthropic"]
    llm_model: str = "llama3.2"
    api_key: Optional[str] = None
    narrative_style: str = "épico e descritivo"
    era: str = "fantasia medieval"
    context: str = "reino em guerra"
    protagonist: str = "um jovem aventureiro"
    characters: str = "magos, guerreiros e criaturas místicas"
    temperature: Optional[float] = 0.8
    max_tokens: Optional[int] = 512
    total_rounds: int = 20
    lang: str = 'pt'

    def model_dump_masked(self) -> dict:
        """Retorna representação com api_key mascarada para logging seguro."""
        data = self.model_dump()
        if data.get('api_key'):
            data['api_key'] = '***'
        return data

class PlayerAction(BaseModel):
    session_id: str
    action: str  # "1", "2", "3" ou texto customizado

class GameResponse(BaseModel):
    session_id: str
    round: int
    narrative: str
    options: List[str]
    is_final: bool = False
    log_file: Optional[str] = None


# ============ ROTAS DA API ============

@app.get("/")
async def root():
    """Serve o frontend"""
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.post("/api/game/start")
async def start_game(setup: GameSetup) -> GameResponse:
    """Inicia uma nova aventura"""
    try:
        config = GameConfig(
            llm_type=setup.llm_type,
            llm_model=setup.llm_model,
            narrative_style=setup.narrative_style,
            era=setup.era,
            context=setup.context,
            protagonist=setup.protagonist,
            characters=setup.characters,
            lang=setup.lang
        )
        
        llm_manager = LLMManager(
            llm_type=setup.llm_type,
            model=setup.llm_model,
            api_key=setup.api_key,
            temperature=setup.temperature or 0.8,
            max_tokens=setup.max_tokens or 512
        )
        
        session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        game_state = GameState(
            config=config,
            session_id=session_id,
            llm_manager=llm_manager,
            total_rounds=setup.total_rounds
        )
        game_store.set(session_id, game_state)
        
        # Gerar introdução
        total_rounds = setup.total_rounds
        rounds_display = f"Rodada 1 de {total_rounds}" if total_rounds > 0 else "Rodada 1 — Modo Livre (Até o fim)"
        lang_instruction = (
            "IMPORTANT: You are narrating this adventure in ENGLISH. All your responses must be in English."
            if setup.lang == 'en' else
            "IMPORTANTE: Você está narrando esta aventura em PORTUGUÊS. Todas as suas respostas devem ser em português."
        )
        intro_prompt = f"""Você é um mestre de RPG narrando uma aventura no estilo dos livros-jogos "Aventuras Fantásticas" (Fighting Fantasy), criados por Ian Livingstone e Steve Jackson.

CONFIGURAÇÃO DA AVENTURA:
- Estilo narrativo: {config.narrative_style}
- Época: {config.era}
- Contexto: {config.context}
- Protagonista: {config.protagonist}
- Personagens do mundo: {config.characters}

IDIOMA:
{lang_instruction}

DIRETRIZES DE NARRATIVA (SIGA RIGOROSAMENTE):

1. TOM LIVRO-JOGO CLÁSSICO:
   - Narre em SEGUNDA PESSOA ("Você")
   - Use parágrafos curtos e impactantes (3-5 frases)
   - Priorize descrições SENSORIAIS (sons, cheiros, texturas, temperaturas)
   - Crie tensão e senso de urgência constantes
   - Cada cena deve evocar perigo, mistério ou maravilha

2. PERSONAGENS RECORRENTES:
   - Os personagens mencionados na configuração ({config.characters}) DEVEM aparecer na história
   - Dê NOMES PRÓPRIOS a pelo menos 2 personagens recorrentes (ex: "Maelon, o mago ancião", "Brynn, a guerreira élfica")
   - Mantenha esses personagens presentes e atuantes ao longo da narrativa
   - Eles devem ter personalidades distintas e motivações claras

3. PROIBIDO (QUEBRA DE IMERSÃO):
   - NUNCA use linguagem moderna, gírias ou referências contemporâneas
   - NUNCA faça metacomentários ("Desculpe, como IA...", "Nesta rodada...", "Aqui está sua aventura...")
   - NUNCA quebre a quarta parede ou mencione que isto é um jogo
   - NUNCA use expressões como "Vamos lá!", "Boa sorte!" ou tom de tutorial
   - Mantenha-se sempre DENTRO do universo da história

Crie a INTRODUÇÃO da aventura ({rounds_display}):
1. Escreva uma introdução envolvente e imersiva (2-3 parágrafos)
2. Descreva a situação inicial do protagonista e o ambiente ao redor
3. Mencione ao menos um personagem do mundo presente na cena
4. Apresente EXATAMENTE 3 opções de ação claras e interessantes
5. Ao apresentar as opções, use frases como "Sua decisão pode mudar tudo" ou "O destino aguarda sua escolha"

Formato de resposta:
[NARRATIVA]
(texto da introdução)

[OPÇÕES]
1. (primeira opção)
2. (segunda opção)
3. (terceira opção)"""

        response = await llm_manager.generate(intro_prompt)
        narrative, options = parse_llm_response(response)
        
        # Salvar no estado
        game_state.add_round(narrative, options, None)
        
        return GameResponse(
            session_id=session_id,
            round=1,
            narrative=narrative,
            options=options,
            is_final=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar jogo: {str(e)}")

@app.post("/api/game/action")
async def process_action(action: PlayerAction) -> GameResponse:
    """Processa uma ação do jogador"""
    try:
        game_state = game_store.get(action.session_id)
        
        if game_state is None:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        # Verificar se o jogo já terminou
        total_rounds = game_state.total_rounds
        if total_rounds > 0 and game_state.current_round >= total_rounds:
            raise HTTPException(status_code=400, detail="Jogo já finalizado")
        
        # Determinar ação escolhida
        last_round = game_state.rounds[-1]
        
        # Se for número, usar opção correspondente
        if action.action in ["1", "2", "3"]:
            chosen_action = last_round["options"][int(action.action) - 1]
        else:
            chosen_action = action.action  # Ação customizada
        
        # Salvar ação escolhida
        game_state.rounds[-1]["player_action"] = chosen_action
        
        # Próxima rodada
        next_round = game_state.current_round + 1
        is_final = (total_rounds > 0 and next_round > total_rounds)
        
        # Gerar próxima narrativa
        if is_final:
            lang_instruction = (
                "IMPORTANT: You are narrating this adventure in ENGLISH. All your responses must be in English."
                if game_state.config.lang == 'en' else
                "IMPORTANTE: Você está narrando esta aventura em PORTUGUÊS. Todas as suas respostas devem ser em português."
            )
            continuation_prompt = f"""Você é um mestre de RPG narrando o desfecho de uma aventura no estilo Fighting Fantasy.

CONFIGURAÇÃO DA AVENTURA:
- Época: {game_state.config.era}
- Contexto: {game_state.config.context}
- Protagonista: {game_state.config.protagonist}
- Personagens do mundo: {game_state.config.characters}

IDIOMA:
{lang_instruction}

RODADA FINAL ({total_rounds}/{total_rounds}) - CONCLUSÃO DA HISTÓRIA

Contexto da história:
{format_history(game_state.rounds[-3:])}

Última ação do jogador: {chosen_action}

DIRETRIZES DE NARRATIVA (SIGA RIGOROSAMENTE):

1. TOM LIVRO-JOGO CLÁSSICO:
   - Narre em SEGUNDA PESSOA ("Você")
   - Parágrafos curtos e impactantes
   - Descrições sensoriais vívidas
   - Tom épico e conclusivo — este é o GRANDE FINAL

2. PERSONAGENS RECORRENTES:
   - Traga os personagens do mundo ({game_state.config.characters}) para o desfecho
   - Mostre o destino dos personagens nomeados que apareceram na jornada
   - Dê a cada um um fechamento coerente com sua trajetória

3. PROIBIDO (QUEBRA DE IMERSÃO):
   - NUNCA use linguagem moderna, gírias ou referências contemporâneas
   - NUNCA faça metacomentários ("Foi uma ótima aventura!", "Espero que tenha gostado...")
   - NUNCA quebre a quarta parede
   - Mantenha-se estritamente dentro do universo da história ATÉ O FIM

Crie a CONCLUSÃO ÉPICA da aventura:
1. Resolva a ação do jogador de forma dramática
2. Conclua todos os arcos narrativos principais
3. Descreva o destino do protagonista e dos personagens recorrentes
4. Dê um fechamento memorável e satisfatório (triunfo, tragédia ou algo entre os dois)
5. NÃO apresente mais opções - esta é a RODADA FINAL

Formato de resposta:
[NARRATIVA]
(texto conclusivo da aventura - 3-4 parágrafos)

[FIM DA AVENTURA]"""
        else:
            lang_instruction = (
                "IMPORTANT: You are narrating this adventure in ENGLISH. All your responses must be in English."
                if game_state.config.lang == 'en' else
                "IMPORTANTE: Você está narrando esta aventura em PORTUGUÊS. Todas as suas respostas devem ser em português."
            )
            continuation_prompt = f"""Você é um mestre de RPG narrando uma aventura no estilo Fighting Fantasy.

CONFIGURAÇÃO DA AVENTURA:
- Época: {game_state.config.era}
- Contexto: {game_state.config.context}
- Protagonista: {game_state.config.protagonist}
- Personagens do mundo: {game_state.config.characters}

IDIOMA:
{lang_instruction}

RODADA {next_round}/{total_rounds}

Contexto recente:
{format_history(game_state.rounds[-2:])}

Última ação do jogador: {chosen_action}

DIRETRIZES DE NARRATIVA (SIGA RIGOROSAMENTE):

1. TOM LIVRO-JOGO CLÁSSICO:
   - Narre em SEGUNDA PESSOA ("Você")
   - Parágrafos curtos e impactantes (3-5 frases)
   - Descrições sensoriais vívidas (sons, cheiros, texturas)
   - Crie tensão — cada ação deve ter consequências significativas

2. PERSONAGENS RECORRENTES:
   - Mantenha os personagens do mundo ({game_state.config.characters}) atuantes
   - Personagens já nomeados DEVEM reaparecer ou ser mencionados
   - Novos personagens devem ter nomes próprios e personalidades marcantes

3. PROIBIDO (QUEBRA DE IMERSÃO):
   - NUNCA use linguagem moderna, gírias, tecnologia contemporânea
   - NUNCA faça metacomentários sobre ser uma IA ou sobre o jogo
   - NUNCA quebre a quarta parede
   - NUNCA use tom de tutorial ("Você pode escolher entre...", "As opções são...")
   - Mantenha-se estritamente dentro do universo da história

Continue a história:
1. Descreva o resultado da ação do jogador de forma imersiva
2. Desenvolva a narrativa com consequências visíveis (2-3 parágrafos)
3. Inclua ao menos um personagem do mundo interagindo na cena
4. Apresente EXATAMENTE 3 novas opções de ação
5. Use frases como "Sua decisão pode mudar tudo" ou "O destino aguarda sua escolha" ao apresentar as opções

Formato de resposta:
[NARRATIVA]
(texto da continuação)

[OPÇÕES]
1. (primeira opção)
2. (segunda opção)
3. (terceira opção)"""

        response = await game_state.llm_manager.generate(continuation_prompt)
        
        if is_final:
            narrative = response.split("[NARRATIVA]")[-1].split("[FIM")[0].strip()
            options = []
        else:
            narrative, options = parse_llm_response(response)
        
        # Salvar no estado
        game_state.add_round(narrative, options, chosen_action)
        
        # Se final, gerar arquivo de log
        log_file = None
        if is_final:
            log_file = generate_log_file(game_state, LOGS_DIR)
        
        return GameResponse(
            session_id=action.session_id,
            round=next_round,
            narrative=narrative,
            options=options,
            is_final=is_final,
            log_file=log_file
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar ação: {str(e)}")

@app.post("/api/game/end")
async def end_game(action: PlayerAction) -> GameResponse:
    """Força a conclusão da aventura na rodada atual"""
    try:
        game_state = game_store.get(action.session_id)
        
        if game_state is None:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        if game_state.rounds:
            game_state.rounds[-1]["player_action"] = "Concluir aventura"
        
        total_rounds = game_state.total_rounds
        final_round = game_state.current_round + 1
        
        lang_instruction = (
            "IMPORTANT: You are narrating this adventure in ENGLISH. All your responses must be in English."
            if game_state.config.lang == 'en' else
            "IMPORTANTE: Você está narrando esta aventura em PORTUGUÊS. Todas as suas respostas devem ser em português."
        )
        continuation_prompt = f"""Você é um mestre de RPG narrando o desfecho de uma aventura no estilo Fighting Fantasy.

CONFIGURAÇÃO DA AVENTURA:
- Época: {game_state.config.era}
- Contexto: {game_state.config.context}
- Protagonista: {game_state.config.protagonist}
- Personagens do mundo: {game_state.config.characters}

IDIOMA:
{lang_instruction}

RODADA FINAL — CONCLUSÃO DA HISTÓRIA

Contexto da história:
{format_history(game_state.rounds[-3:])}

Última ação do jogador: Decidiu concluir a aventura

DIRETRIZES DE NARRATIVA (SIGA RIGOROSAMENTE):

1. TOM LIVRO-JOGO CLÁSSICO:
   - Narre em SEGUNDA PESSOA ("Você")
   - Parágrafos curtos e impactantes
   - Descrições sensoriais vívidas
   - Tom épico e conclusivo — este é o GRANDE FINAL

2. PERSONAGENS RECORRENTES:
   - Traga os personagens do mundo ({game_state.config.characters}) para o desfecho
   - Mostre o destino dos personagens nomeados que apareceram na jornada
   - Dê a cada um um fechamento coerente com sua trajetória

3. PROIBIDO (QUEBRA DE IMERSÃO):
   - NUNCA use linguagem moderna, gírias ou referências contemporâneas
   - NUNCA faça metacomentários ("Foi uma ótima aventura!", "Espero que tenha gostado...")
   - NUNCA quebre a quarta parede
   - Mantenha-se estritamente dentro do universo da história ATÉ O FIM

Crie a CONCLUSÃO ÉPICA da aventura:
1. Resolva a situação atual de forma dramática e satisfatória
2. Conclua todos os arcos narrativos principais
3. Descreva o destino do protagonista e dos personagens recorrentes
4. Dê um fechamento memorável e satisfatório (triunfo, tragédia ou algo entre os dois)
5. NÃO apresente mais opções - esta é a CONCLUSÃO FINAL

Formato de resposta:
[NARRATIVA]
(texto conclusivo da aventura - 3-4 parágrafos)

[FIM DA AVENTURA]"""

        response = await game_state.llm_manager.generate(continuation_prompt)
        narrative = response.split("[NARRATIVA]")[-1].split("[FIM")[0].strip()
        
        game_state.add_round(narrative, [], "Concluir aventura")
        
        log_file = generate_log_file(game_state, LOGS_DIR)
        
        return GameResponse(
            session_id=action.session_id,
            round=final_round,
            narrative=narrative,
            options=[],
            is_final=True,
            log_file=log_file
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao concluir aventura: {str(e)}")

@app.get("/api/logs/{filename}")
async def download_log(filename: str):
    """Download do arquivo de log com sanitização de path."""
    # Sanitizar: apenas alfanumérico, underscore, hífen, ponto
    safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '', filename)
    if not safe_name or not safe_name.endswith('.md'):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    file_path = (LOGS_DIR / safe_name).resolve()
    logs_resolved = LOGS_DIR.resolve()
    try:
        file_path.relative_to(logs_resolved)
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(file_path, filename=safe_name)

@app.get("/api/ollama/models")
async def list_ollama_models():
    """Retorna a lista de modelos disponíveis no Ollama local"""
    ollama_url = "http://localhost:11434"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return {"models": models}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama não está rodando. Inicie com: ollama serve")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Ollama: {str(e)}")

@app.get("/app.js")
async def serve_js():
    return FileResponse(str(FRONTEND_DIR / "app.js"))

@app.get("/favicon.ico")
async def favicon():
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
        <rect width="32" height="32" fill="#000"/>
        <text x="4" y="24" font-family="monospace" font-size="20" fill="#33ff33" font-weight="bold">&gt;_</text>
    </svg>'''
    return Response(content=svg_content, media_type="image/svg+xml")


# ============ INICIALIZAÇÃO ============

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
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Permite acesso externo
        port=8000,
        reload=True
    )
