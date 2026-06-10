"""Tests for text parsing utilities."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from utils.text_parsers import parse_llm_response, format_history, smart_truncate


class TestParseLLMResponse:
    def test_standard_format(self):
        response = """[NARRATIVA]
Você entra na caverna escura.

[OPÇÕES]
1. Acender uma tocha
2. Voltar para a entrada
3. Gritar por ajuda"""
        narrative, options = parse_llm_response(response)
        assert "caverna escura" in narrative
        assert len(options) == 3
        assert options[0] == "Acender uma tocha"
        assert options[1] == "Voltar para a entrada"
        assert options[2] == "Gritar por ajuda"

    def test_english_markers(self):
        response = """[NARRATIVE]
You enter the dark cave.

[OPTIONS]
1. Light a torch
2. Go back
3. Call for help"""
        narrative, options = parse_llm_response(response)
        assert "dark cave" in narrative
        assert len(options) == 3
        assert "Light a torch" in options[0]

    def test_dash_options(self):
        response = """[NARRATIVA]
Teste

[OPÇÕES]
- Primeira opção
- Segunda opção
- Terceira opção"""
        _, options = parse_llm_response(response)
        assert len(options) == 3
        assert options[0] == "Primeira opção"

    def test_parenthesis_numbering(self):
        response = """[NARRATIVA]
Teste

[OPÇÕES]
1) Opção um
2) Opção dois
3) Opção três"""
        _, options = parse_llm_response(response)
        assert len(options) == 3
        assert options[0] == "Opção um"

    def test_no_options_marker(self):
        response = "Apenas uma narrativa simples sem opções."
        narrative, options = parse_llm_response(response)
        assert "narrativa simples" in narrative
        assert len(options) == 3
        assert all(isinstance(o, str) and len(o) > 0 for o in options)

    def test_empty_response(self):
        narrative, options = parse_llm_response("")
        assert len(options) == 3
        assert all(isinstance(o, str) and len(o) > 0 for o in options)

    def test_no_narrative_marker(self):
        response = """Texto livre qualquer

[OPÇÕES]
1. Opção A
2. Opção B
3. Opção C"""
        narrative, options = parse_llm_response(response)
        assert len(options) == 3
        assert "Opção A" in options[0]

    def test_mixed_newlines(self):
        response = "[NARRATIVA]\r\nLinha 1\r\nLinha 2\r\n\r\n[OPÇÕES]\r\n1. A\r\n2. B\r\n3. C"
        narrative, options = parse_llm_response(response)
        assert "Linha 1" in narrative
        assert len(options) == 3

    def test_fewer_than_three_options(self):
        response = """[NARRATIVA]
Teste

[OPÇÕES]
1. Única opção"""
        _, options = parse_llm_response(response)
        assert len(options) == 3
        assert options[0] == "Única opção"


class TestFormatHistory:
    def test_basic_formatting(self):
        rounds = [
            {
                "round_number": 1,
                "narrative": "Você acorda em uma floresta.",
                "player_action": "Olhar ao redor"
            }
        ]
        result = format_history(rounds, max_tokens_approx=100)
        assert "Rodada 1" in result
        assert "floresta" in result
        assert "Olhar ao redor" in result

    def test_empty_rounds(self):
        assert format_history([], max_tokens_approx=100) == ""

    def test_respects_token_limit(self):
        rounds = [
            {
                "round_number": i,
                "narrative": "X" * 500,
                "player_action": "ação"
            }
            for i in range(1, 10)
        ]
        result = format_history(rounds, max_tokens_approx=100)
        assert len(result) < 9 * 600

    def test_recent_rounds_prioritized(self):
        rounds = [
            {
                "round_number": i,
                "narrative": f"Rodada número {i}",
                "player_action": None
            }
            for i in range(1, 6)
        ]
        result = format_history(rounds, max_tokens_approx=10)
        assert "Rodada 5" in result


class TestSmartTruncate:
    def test_no_truncation_needed(self):
        assert smart_truncate("Curto", 100) == "Curto"

    def test_truncates_at_word_boundary(self):
        result = smart_truncate("uma frase muito longa para caber", 15)
        assert not result.endswith("lon")
        assert len(result) <= 15

    def test_fallback_to_hard_truncation(self):
        result = smart_truncate("palavraquenaotemespacos", 5)
        assert len(result) <= 5
