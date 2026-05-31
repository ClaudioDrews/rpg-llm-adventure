"""
Game State - Gerenciamento do estado do jogo
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class GameConfig:
    """Configuração da aventura"""
    llm_type: str
    llm_model: str
    api_key: Optional[str]
    narrative_style: str
    era: str
    context: str
    protagonist: str
    characters: str


@dataclass
class GameState:
    """Estado completo de uma sessão de jogo"""
    config: GameConfig
    session_id: str
    current_round: int = 0
    rounds: List[dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    
    def add_round(self, narrative: str, options: List[str], player_action: Optional[str] = None):
        """Adiciona uma nova rodada ao histórico"""
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
        return self.current_round >= 20
