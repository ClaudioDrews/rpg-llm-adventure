"""Game session store with TTL-based cleanup."""
import asyncio
import time
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game_state import GameState


class GameStore:
    """Armazena sessões ativas com TTL e cleanup automático."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._games: Dict[str, tuple["GameState", float]] = {}
        self._ttl = ttl_seconds
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start_cleanup(self):
        """Inicia o loop de cleanup em background."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup(self):
        """Para o loop de cleanup."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    def get(self, session_id: str) -> Optional["GameState"]:
        """Retorna o GameState e renova TTL."""
        if session_id in self._games:
            state, _ = self._games[session_id]
            self._games[session_id] = (state, time.time())
            return state
        return None
    
    def set(self, session_id: str, state: "GameState"):
        """Armazena ou atualiza uma sessão."""
        self._games[session_id] = (state, time.time())
    
    def remove(self, session_id: str):
        """Remove uma sessão explicitamente."""
        self._games.pop(session_id, None)
    
    def __contains__(self, session_id: str) -> bool:
        return session_id in self._games
    
    async def _cleanup_loop(self):
        """Remove sessões expiradas a cada 5 minutos."""
        while True:
            await asyncio.sleep(300)
            now = time.time()
            expired = [
                sid for sid, (_, ts) in self._games.items()
                if now - ts > self._ttl
            ]
            for sid in expired:
                del self._games[sid]
