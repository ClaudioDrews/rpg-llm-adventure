"""Log file generation for completed adventures."""
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from game_state import GameState

import yaml


def generate_log_file(game_state: "GameState", logs_dir: Path) -> str:
    """Gera arquivo de log da aventura em Markdown com frontmatter YAML.
    
    Retorna o nome do arquivo (não o path completo).
    """
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    filename = f"aventura_{game_state.session_id}.md"
    filepath = logs_dir / filename

    total_rounds = len(game_state.rounds)
    c = game_state.config

    # YAML frontmatter com escaping correto via PyYAML
    frontmatter = {
        "title": "Aventura Fantástica",
        "date": data_atual,
        "session": game_state.session_id,
        "llm_type": c.llm_type,
        "llm_model": c.llm_model,
        "narrative_style": c.narrative_style,
        "era": c.era,
        "context": c.context,
        "protagonist": c.protagonist,
        "characters": c.characters,
        "total_rounds": total_rounds,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\n")
        yaml.dump(frontmatter, f, allow_unicode=True, default_flow_style=False)
        f.write("---\n\n")

        f.write("# Aventura Fantástica\n\n")
        f.write(f"**Data:** {data_atual}  \n")
        f.write(f"**Sessão:** {game_state.session_id}\n\n")

        f.write("## Configuração da Aventura\n\n")
        f.write(f"| Campo | Valor |\n")
        f.write(f"|-------|-------|\n")
        f.write(f"| Estilo Narrativo | {c.narrative_style} |\n")
        f.write(f"| Época | {c.era} |\n")
        f.write(f"| Contexto | {c.context} |\n")
        f.write(f"| Protagonista | {c.protagonist} |\n")
        f.write(f"| Personagens | {c.characters} |\n")
        f.write(f"| LLM | {c.llm_type} ({c.llm_model}) |\n\n")

        for i, round_data in enumerate(game_state.rounds, 1):
            is_last = (i == total_rounds)

            if is_last:
                f.write("---\n\n")
                f.write("## Conclusão\n\n")
            else:
                f.write(f"### Rodada {i}/{total_rounds}\n\n")

            f.write(round_data['narrative'])
            f.write("\n\n")

            if round_data['options']:
                f.write("**Opções:**\n\n")
                for j, option in enumerate(round_data['options'], 1):
                    f.write(f"{j}. {option}\n")
                f.write("\n")

            if round_data['player_action']:
                f.write(f"> **Ação do jogador:** {round_data['player_action']}\n\n")

        f.write("\n---\n")
        f.write("*Fim da aventura — gerado por RPG LLM Adventure*\n")

    return filename
