import pytest
from app.providers.factory import get_llm_provider, GroundedFallbackProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider, OpenAIProvider

def test_provider_factory_resolution():
    ollama_prov = get_llm_provider("ollama")
    assert isinstance(ollama_prov, OllamaProvider)

@pytest.mark.asyncio
async def test_cloud_provider_graceful_missing_key():
    prov = ClaudeProvider(api_key="")
    chunks = []
    async for token in prov.generate_response(
        messages=[{"role": "user", "content": "Hello"}],
        system_prompt="Test"
    ):
        chunks.append(token)
    full_output = "".join(chunks)
    assert "Anthropic Claude API Key Missing" in full_output

@pytest.mark.asyncio
async def test_grounded_fallback_provider_out_of_domain():
    fallback = GroundedFallbackProvider()
    chunks = []
    async for token in fallback.generate_response(
        messages=[{"role": "user", "content": "How to make lasagna?"}],
        system_prompt="INSUFFICIENT_CONTEXT_REFUSAL"
    ):
        chunks.append(token)
    full_output = "".join(chunks)
    assert "I do not have sufficient information in Lenny's podcast archive to answer this." in full_output
