"""
Game State - Gerenciamento do estado do jogo
"""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING, Any
from datetime import datetime

if TYPE_CHECKING:
    from llm_manager import LLMManager

MAX_ROUNDS_FREE_MODE = 100  # sanity limit para modo "Até o fim"


@dataclass
class GameConfig:
    """Configuração da aventura"""
    llm_type: str
    llm_model: str
    narrative_style: str
    era: str
    context: str
    protagonist: str
    characters: str
    lang: str = 'pt'


@dataclass
class GameState:
    """Estado completo de uma sessão de jogo"""
    config: GameConfig
    session_id: str
    llm_manager: Any = None  # LLMManager instance, set after creation
    current_round: int = 0
    rounds: List[dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    total_rounds: int = 20  # 0 significa modo 'Até o fim'
    
    def add_round(
        self,
        narrative: str,
        options: List[str],
        player_action: Optional[str] = None
    ):
        """Adiciona uma nova rodada ao histórico."""
        if self.total_rounds == 0 and self.current_round >= MAX_ROUNDS_FREE_MODE:
            raise ValueError(
                f"Limite de segurança do modo livre atingido "
                f"({MAX_ROUNDS_FREE_MODE} rodadas)"
            )
        self.current_round += 1
        self.rounds.append({
            "round_number": self.current_round,
            "narrative": narrative,
            "options": options,
            "player_action": player_action,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_history(self, last_n: int = 3) -> List[dict]:
        """Retorna as últimas N rodadas"""
        return self.rounds[-last_n:] if self.rounds else []
    
    def is_complete(self) -> bool:
        """Verifica se o jogo está completo"""
        if self.total_rounds == 0:
            return False  # Modo 'Até o fim' nunca termina por contagem
        return self.current_round >= self.total_rounds
