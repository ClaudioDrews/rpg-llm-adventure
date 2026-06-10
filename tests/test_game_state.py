"""Tests for GameState model."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from game_state import GameState, GameConfig, MAX_ROUNDS_FREE_MODE


@pytest.fixture
def base_config():
    return GameConfig(
        llm_type="ollama",
        llm_model="test-model",
        narrative_style="épico",
        era="fantasia medieval",
        context="reino em guerra",
        protagonist="herói",
        characters="dragão ancião",
        lang="pt"
    )


@pytest.fixture
def game_state(base_config):
    return GameState(
        config=base_config,
        session_id="test_session_001",
        total_rounds=5
    )


class TestGameStateCreation:
    def test_initial_state(self, game_state):
        assert game_state.current_round == 0
        assert len(game_state.rounds) == 0
        assert game_state.session_id == "test_session_001"
        assert game_state.total_rounds == 5

    def test_default_total_rounds(self, base_config):
        gs = GameState(config=base_config, session_id="test")
        assert gs.total_rounds == 20


class TestAddRound:
    def test_increments_round_number(self, game_state):
        game_state.add_round("Narrativa 1", ["Op1", "Op2", "Op3"])
        assert game_state.current_round == 1
        assert len(game_state.rounds) == 1
        
        game_state.add_round("Narrativa 2", ["A", "B", "C"])
        assert game_state.current_round == 2
        assert len(game_state.rounds) == 2

    def test_stores_round_data(self, game_state):
        game_state.add_round(
            "Uma grande narrativa",
            ["Opção A", "Opção B", "Opção C"],
            player_action="Opção A"
        )
        round_data = game_state.rounds[0]
        assert round_data["round_number"] == 1
        assert round_data["narrative"] == "Uma grande narrativa"
        assert round_data["options"] == ["Opção A", "Opção B", "Opção C"]
        assert round_data["player_action"] == "Opção A"
        assert "timestamp" in round_data


class TestIsComplete:
    def test_not_complete_before_limit(self, game_state):
        game_state.add_round("R1", ["a", "b", "c"])
        assert not game_state.is_complete()

    def test_complete_at_limit(self, game_state):
        for i in range(5):
            game_state.add_round(f"R{i+1}", ["a", "b", "c"])
        assert game_state.is_complete()

    def test_not_complete_in_free_mode(self, base_config):
        gs = GameState(config=base_config, session_id="free", total_rounds=0)
        gs.add_round("R1", ["a", "b", "c"])
        assert not gs.is_complete()

    def test_free_mode_never_completes(self, base_config):
        gs = GameState(config=base_config, session_id="free", total_rounds=0)
        for i in range(99):
            gs.add_round(f"R{i+1}", ["a", "b", "c"])
        assert not gs.is_complete()

    def test_negative_total_rounds_treated_as_free(self, base_config):
        gs = GameState(config=base_config, session_id="neg", total_rounds=-1)
        gs.add_round("R1", ["a", "b", "c"])
        assert not gs.is_complete()


class TestSanityLimit:
    def test_free_mode_raises_at_limit(self, base_config):
        gs = GameState(config=base_config, session_id="max", total_rounds=0)
        for i in range(MAX_ROUNDS_FREE_MODE):
            gs.add_round(f"R{i+1}", ["a", "b", "c"])
        assert gs.current_round == MAX_ROUNDS_FREE_MODE
        
        with pytest.raises(ValueError, match="Limite de segurança"):
            gs.add_round("Extra", ["x", "y", "z"])

    def test_normal_mode_no_sanity_limit(self, base_config):
        gs = GameState(config=base_config, session_id="normal", total_rounds=200)
        for i in range(150):
            gs.add_round(f"R{i+1}", ["a", "b", "c"])
        assert gs.current_round == 150
