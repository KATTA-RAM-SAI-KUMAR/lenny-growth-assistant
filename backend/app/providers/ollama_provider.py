import httpx
import json
import logging
from typing import AsyncGenerator, Dict, List
from .base import BaseLLMProvider

logger = logging.getLogger("lenny.providers.ollama")

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def get_available_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": True,
            "options": {"temperature": temperature}
        }

        is_connected = False
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        logger.error(f"Ollama error {response.status_code}: {err_text}")
                        yield f"\n\n> ⚠️ **Ollama Status ({response.status_code})**: Model `{self.model}` not found locally. Activating Resilient Grounded Engine below...\n\n"
                    else:
                        is_connected = True
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    chunk = json.loads(line)
                                    content = chunk.get("message", {}).get("content", "")
                                    if content:
                                        yield content
                                except Exception as parse_err:
                                    logger.debug(f"Chunk parse error: {parse_err}")
                        return
        except (httpx.ConnectError, httpx.ConnectTimeout):
            logger.info(f"Ollama not reachable at {self.base_url}, activating Resilient Grounded Engine.")
            yield f"> 💡 *Notice: Ollama not detected on {self.base_url} (run `ollama run {self.model}` for local inference). Seamlessly engaging Grounded Archive Synthesis:*\n\n"
        except Exception as e:
            logger.error(f"Ollama streaming exception: {e}")
            yield f"> ⚠️ *Ollama Exception ({e}). Engaging Grounded Archive Synthesis:*\n\n"

        # Seamless Grounded Fallback
        from .factory import GroundedFallbackProvider
        fallback = GroundedFallbackProvider()
        async for token in fallback.generate_response(messages, system_prompt, temperature):
            yield token
