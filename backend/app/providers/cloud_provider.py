import logging
from typing import AsyncGenerator, Dict, List

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from .base import BaseLLMProvider

logger = logging.getLogger("lenny.providers.cloud")


class ClaudeProvider(BaseLLMProvider):
    """Claude provider implemented through the Anthropic Claude Agent SDK."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model

    async def check_health(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield (
                "\n\n> ?? **Anthropic Claude API Key Missing**: "
                "Please configure `ANTHROPIC_API_KEY` in your `.env` file.\n"
                "> You can switch to **Ollama** via the model selector in the top bar."
            )
            return

        # The SDK reads ANTHROPIC_API_KEY from the environment.
        # Set it here so the provider remains compatible with the existing
        # application configuration.
        import os
        os.environ["ANTHROPIC_API_KEY"] = self.api_key

        try:
            options = ClaudeAgentOptions(
                model=self.model,
                system_prompt=system_prompt,
                max_turns=1,
                permission_mode="bypassPermissions",
            )

            # Convert the existing conversation history into a single
            # grounded prompt while preserving the latest user request.
            conversation = "\n\n".join(
                f"{m['role'].upper()}: {m['content']}"
                for m in messages
                if m.get("role") in {"user", "assistant"}
            )

            prompt = (
                "Answer the user's request using the provided system instructions "
                "and transcript evidence. Do not use external information.\n\n"
                f"Conversation:\n{conversation}"
            )

            client = ClaudeSDKClient(options)

            async with client:
                await client.query(prompt)

                async for message in client.receive_response():
                    # AssistantMessage contains the model's generated content.
                    if message.__class__.__name__ == "AssistantMessage":
                        for block in getattr(message, "content", []):
                            text = getattr(block, "text", None)
                            if text:
                                yield text

        except Exception as e:
            logger.exception("Claude Agent SDK streaming exception")
            yield (
                "\n\n> ?? **Claude Agent Error**: "
                "Unable to generate a response. Please try Ollama or try again."
            )


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model

    async def check_health(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield (
                "\n\n> ?? **OpenAI API Key Missing**: "
                "Please configure `OPENAI_API_KEY` in your `.env` file.\n"
                "> You can switch to **Ollama** via the model selector in the top bar."
            )
            return

        import httpx
        import json

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        openai_messages = [{"role": "system", "content": system_prompt}] + [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ["user", "assistant"]
        ]

        payload = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                ) as response:
                    if response.status_code != 200:
                        logger.error(
                            "OpenAI API error %s",
                            response.status_code,
                        )
                        yield (
                            "\n\n> ?? **OpenAI API Error**: "
                            "The cloud provider could not generate a response."
                        )
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()

                            if data_str == "[DONE]":
                                break

                            try:
                                chunk = json.loads(data_str)
                                delta = chunk.get("choices", [{}])[0].get(
                                    "delta", {}
                                )
                                content = delta.get("content", "")

                                if content:
                                    yield content
                            except Exception:
                                continue

        except Exception:
            logger.exception("OpenAI streaming exception")
            yield (
                "\n\n> ?? **OpenAI Connection Error**: "
                "Unable to connect to the cloud provider."
            )
