#!/usr/bin/env python3
"""
RPG LLM Adventure - Interface de Terminal (CLI)
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
import asyncio
from llm_manager import LLMManager
from game_state import GameState, GameConfig
from utils.text_parsers import parse_llm_response, format_history, smart_truncate
from datetime import datetime
import textwrap


class TerminalUI:
    def __init__(self):
        self.llm_manager = None  # Será configurado em setup_game()
        self.game_state = None
        self.width = 80
    
    def clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self, text: str):
        print("\n" + "=" * self.width)
        print(text.center(self.width))
        print("=" * self.width + "\n")
    
    def print_section(self, text: str):
        print("\n" + "-" * self.width)
        print(text)
        print("-" * self.width + "\n")
    
    def print_wrapped(self, text: str):
        wrapped = textwrap.fill(text, width=self.width)
        print(wrapped)
    
    def input_choice(self, prompt: str, valid_choices: list) -> str:
        while True:
            choice = input(f"\n{prompt}: ").strip()
            if choice in valid_choices or choice in [str(i) for i in range(1, len(valid_choices) + 1)]:
                return choice
            print(f"❌ Opção inválida. Escolha entre: {', '.join(valid_choices)}")
    
    async def setup_game(self):
        self.clear()
        self.print_header("🎲 RPG LLM ADVENTURE - CONFIGURAÇÃO")
        print("Bem-vindo à sua aventura fantástica!\n")
        print("1. Qual LLM você deseja usar?")
        print("   1. Ollama (Local)")
        print("   2. OpenAI API")
        print("   3. Anthropic API")
        llm_choice = self.input_choice("Escolha", ["1", "2", "3"])
        llm_types = {"1": ("ollama", "llama3.2"), "2": ("openai", "gpt-4o-mini"), "3": ("anthropic", "claude-sonnet-4-20250514")}
        llm_type, default_model = llm_types[llm_choice]
        model = input(f"\nModelo [{default_model}]: ").strip() or default_model
        api_key = None
        if llm_type in ["openai", "anthropic"]:
            api_key = input(f"\nAPI Key para {llm_type}: ").strip()
            if not api_key:
                print("❌ API Key é obrigatória!")
                sys.exit(1)
        try:
            # Bug A corrigido: LLMManager recebe tudo no __init__, sem configure()
            self.llm_manager = LLMManager(
                llm_type=llm_type,
                model=model,
                api_key=api_key
            )
            print(f"\n✅ LLM configurado: {llm_type} ({model})")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            sys.exit(1)
        self.print_section("CONFIGURAÇÃO DA AVENTURA")
        print("Personalize sua aventura:\n")
        narrative_style = input("Estilo narrativo [épico e descritivo]: ").strip() or "épico e descritivo"
        era = input("Época [fantasia medieval]: ").strip() or "fantasia medieval"
        context = input("Contexto [reino em guerra]: ").strip() or "reino em guerra"
        protagonist = input("Protagonista [um jovem aventureiro]: ").strip() or "um jovem aventureiro"
        characters = input("Personagens [magos, guerreiros e criaturas]: ").strip() or "magos, guerreiros e criaturas místicas"
        
        # Bug B corrigido: GameConfig não aceita api_key
        config = GameConfig(
            llm_type=llm_type,
            llm_model=model,
            narrative_style=narrative_style,
            era=era,
            context=context,
            protagonist=protagonist,
            characters=characters
        )
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.game_state = GameState(
            config=config,
            session_id=session_id,
            llm_manager=self.llm_manager
        )
        print("\n✅ Configuração concluída!")
        input("\nPressione ENTER para começar a aventura...")
    
    async def start_adventure(self):
        self.clear()
        self.print_header("🎲 INÍCIO DA AVENTURA")
        print("Gerando a história inicial...\n")
        config = self.game_state.config
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
        response = await self.llm_manager.generate(intro_prompt, max_tokens=1500)
        narrative, options = parse_llm_response(response)
        self.game_state.add_round(narrative, options)
        self._display_round(narrative, options, 1)
    
    async def play_round(self):
        current_round = self.game_state.current_round
        last_round = self.game_state.rounds[-1]
        print("\n" + "=" * self.width)
        print("O que você faz?")
        print(f"Digite 1, 2 ou 3 para escolher uma opção, ou descreva sua própria ação:")
        action = input("\n> ").strip()
        if action in ["1", "2", "3"]:
            chosen_action = last_round["options"][int(action) - 1]
            print(f"\n✓ Você escolheu: {chosen_action}")
        else:
            chosen_action = action
            print(f"\n✓ Ação customizada: {chosen_action}")
        self.game_state.rounds[-1]["player_action"] = chosen_action
        next_round = current_round + 1
        is_final = (self.game_state.total_rounds > 0 and next_round > self.game_state.total_rounds)
        print("\n⏳ Gerando continuação...\n")
        if is_final:
            prompt = self._create_final_prompt(chosen_action)
        else:
            prompt = self._create_continuation_prompt(chosen_action, next_round)
        response = await self.llm_manager.generate(prompt, max_tokens=1500)
        if is_final:
            narrative = response.split("[NARRATIVA]")[-1].split("[FIM")[0].strip()
            options = []
        else:
            narrative, options = parse_llm_response(response)
        self.game_state.add_round(narrative, options)
        self.clear()
        self._display_round(narrative, options, next_round, is_final)
        return is_final
    
    def _display_round(self, narrative: str, options: list, round_num: int, is_final: bool = False):
        total = self.game_state.total_rounds
        rounds_str = f"{total}" if total > 0 else "∞"
        self.print_header(f"{'FIM DA' if is_final else ''} AVENTURA - RODADA {round_num}/{rounds_str}")
        self.print_wrapped(narrative)
        if options:
            self.print_section("OPÇÕES")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
    
    def _create_continuation_prompt(self, action: str, round_num: int) -> str:
        total = self.game_state.total_rounds
        rounds_str = f"{total}" if total > 0 else "∞"
        history = format_history(self.game_state.rounds[-2:])
        return f"""Continue a aventura de RPG (estilo Fighting Fantasy).

RODADA {round_num}/{rounds_str}

Contexto recente:
{history}

Última ação do jogador: {action}

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
    
    def _create_final_prompt(self, action: str) -> str:
        total = self.game_state.total_rounds
        rounds_str = f"{total}" if total > 0 else "∞"
        history = format_history(self.game_state.rounds[-3:])
        return f"""Continue a aventura de RPG (estilo Fighting Fantasy).

RODADA FINAL ({rounds_str}/{rounds_str}) - CONCLUSÃO DA HISTÓRIA

Contexto da história:
{history}

Última ação do jogador: {action}

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

    def save_log(self):
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        filename = f"aventura_{self.game_state.session_id}.txt"
        filepath = logs_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("AVENTURA FANTÁSTICA - LOG COMPLETO\n")
            f.write("=" * 80 + "\n\n")
            config = self.game_state.config
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Sessão: {self.game_state.session_id}\n\n")
            f.write("CONFIGURAÇÃO:\n")
            f.write("-" * 80 + "\n")
            f.write(f"Estilo: {config.narrative_style}\n")
            f.write(f"Época: {config.era}\n")
            f.write(f"Contexto: {config.context}\n")
            f.write(f"Protagonista: {config.protagonist}\n")
            f.write(f"Personagens: {config.characters}\n")
            f.write(f"LLM: {config.llm_type} ({config.llm_model})\n\n")
            f.write("=" * 80 + "\n")
            f.write("A AVENTURA\n")
            f.write("=" * 80 + "\n\n")
            for i, round_data in enumerate(self.game_state.rounds, 1):
                total = self.game_state.total_rounds
                rounds_str = f"{total}" if total > 0 else "∞"
                f.write(f"\n{'=' * 80}\n")
                f.write(f"RODADA {i}/{rounds_str}\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(round_data['narrative'])
                f.write("\n\n")
                if round_data['options']:
                    f.write("OPÇÕES:\n")
                    for j, option in enumerate(round_data['options'], 1):
                        f.write(f"{j}. {option}\n")
                    f.write("\n")
                if round_data['player_action']:
                    f.write(f">>> AÇÃO: {round_data['player_action']}\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("FIM DA AVENTURA\n")
            f.write("=" * 80 + "\n")
        return filepath


async def main():
    ui = TerminalUI()
    try:
        await ui.setup_game()
        await ui.start_adventure()
        while True:
            is_final = await ui.play_round()
            if is_final:
                break
            # Free mode (total_rounds <= 0) never ends by round count;
            # sanity limit em GameState.add_round() bloqueia em 100 rodadas
        ui.print_section("SALVANDO AVENTURA")
        log_path = ui.save_log()
        print(f"✅ Log salvo em: {log_path}")
        print("\n🎉 Obrigado por jogar!")
    except KeyboardInterrupt:
        print("\n\n👋 Jogo interrompido. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
