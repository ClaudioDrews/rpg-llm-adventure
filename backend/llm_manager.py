"""
LLM Manager - Gerenciador de modelos locais e APIs
Suporta: Ollama (local), OpenAI API, Anthropic API
"""

import httpx
import os
from typing import Optional, Literal
import json


class LLMManager:
    """Gerencia conexões com diferentes provedores de LLM"""
    
    def __init__(
        self,
        llm_type: Literal["ollama", "openai", "anthropic"],
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.8,
        max_tokens: int = 512
    ):
        self.llm_type = llm_type
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.ollama_url = "http://localhost:11434"

        # Verificar disponibilidade
        if llm_type == "ollama":
            self._check_ollama()
        elif llm_type in ["openai", "anthropic"] and not api_key:
            raise ValueError(f"API key necessária para {llm_type}")
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Gera texto usando o LLM configurado"""
        if self.llm_type == "ollama":
            return await self._generate_ollama(prompt, max_tokens)
        elif self.llm_type == "openai":
            return await self._generate_openai(prompt, max_tokens)
        elif self.llm_type == "anthropic":
            return await self._generate_anthropic(prompt, max_tokens)
        else:
            raise ValueError(f"Tipo de LLM não suportado: {self.llm_type}")
    
    async def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        """Gera usando Ollama local"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": self.temperature,
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["response"]
            except httpx.ConnectError:
                raise ConnectionError(
                    "Não foi possível conectar ao Ollama. "
                    "Verifique se o Ollama está rodando: ollama serve"
                )
            except Exception as e:
                raise Exception(f"Erro ao gerar com Ollama: {str(e)}")
    
    async def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        """Gera usando OpenAI API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": self.temperature
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ValueError("API key da OpenAI inválida")
                raise Exception(f"Erro da API OpenAI: {e.response.text}")
            except Exception as e:
                raise Exception(f"Erro ao gerar com OpenAI: {str(e)}")
    
    async def _generate_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Gera usando Anthropic API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": self.temperature
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ValueError("API key da Anthropic inválida")
                raise Exception(f"Erro da API Anthropic: {e.response.text}")
            except Exception as e:
                raise Exception(f"Erro ao gerar com Anthropic: {str(e)}")
    
    def _check_ollama(self):
        """Verifica se Ollama está disponível"""
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                response.raise_for_status()
        except:
            raise ConnectionError(
                "Ollama não está rodando. Inicie com: ollama serve"
            )
    
    def list_ollama_models(self) -> list:
        """Lista modelos disponíveis no Ollama"""
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            return []
