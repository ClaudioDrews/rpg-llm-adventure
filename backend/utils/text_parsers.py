"""Text parsing and formatting utilities for LLM responses and history."""
import re
from typing import List, Tuple


def parse_llm_response(response: str) -> Tuple[str, List[str]]:
    """Extrai narrativa e opções da resposta da LLM com parsing robusto.
    
    Aceita múltiplos formatos de marcadores e numeração de opções.
    Fallback heurístico quando o formato esperado não é encontrado.
    Sempre retorna 3 opções.
    """
    text = response.replace('\r\n', '\n')
    
    # Extrair narrativa
    narrative_match = re.search(
        r'\[NARRATIVA\]\s*(.*?)(?=\[(?:OPÇÕES|OPTIONS|FIM)|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    narrative = narrative_match.group(1).strip() if narrative_match else text.strip()
    
    # Extrair opções
    options = []
    options_match = re.search(
        r'\[(?:OPÇÕES|OPTIONS)\]\s*(.*?)(?=\[FIM|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    if options_match:
        options_text = options_match.group(1)
        option_pattern = (
            r'(?:^|\n)\s*'
            r'(?:\d+[\.\)]\s*|[-*]\s*)'
            r'\s*(.+?)'
            r'(?=(?:\n\s*(?:\d+[\.\)]|[-*]\s))|\Z)'
        )
        options = [
            m.strip()
            for m in re.findall(option_pattern, options_text, re.MULTILINE)
            if m.strip()
        ]
    
    # Fallback heurístico
    if not options:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            candidate_lines = [
                l for l in lines[-5:]
                if len(l) < 100 and not l.endswith('.')
            ]
            if len(candidate_lines) >= 3:
                options = candidate_lines[-3:]
                if len(lines) > 3:
                    narrative = '\n'.join(lines[:-3])
    
    # Garantir 3 opções
    fallback_options = [
        "Investigar mais a fundo",
        "Seguir em frente com cautela",
        "Tentar uma abordagem diferente"
    ]
    
    final_options = options[:3]
    while len(final_options) < 3:
        final_options.append(fallback_options[len(final_options)])
    
    return narrative, final_options


def format_history(rounds: List[dict], max_tokens_approx: int = 1500) -> str:
    """Formata histórico de rodadas respeitando janela de contexto.
    
    Prioriza rodadas mais recentes. Aproximação: ~4 chars por token.
    """
    if not rounds:
        return ""
    
    history_parts = []
    total_chars = 0
    max_chars = max_tokens_approx * 4
    
    for r in reversed(rounds):
        entry = f"Rodada {r['round_number']}:\n{r['narrative']}\n"
        if r.get('player_action'):
            entry += f"Ação: {r['player_action']}\n"
        entry += "---\n"
        
        if total_chars + len(entry) > max_chars and history_parts:
            break
        
        history_parts.insert(0, entry)
        total_chars += len(entry)
    
    return "\n".join(history_parts)


def smart_truncate(text: str, max_chars: int) -> str:
    """Trunca texto em limite de palavra, preservando palavras inteiras."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars // 2:
        return text[:last_space]
    return truncated
