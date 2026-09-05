from app.skills.ship30_writer import build_ship30_prompt
from app.skills.grounded_chat import build_grounded_system_prompt
from app.skills.artifact_generator import extract_artifacts


def test_ship30_prompt_structure():
    chunks = [{
        "episode": "Brian Chesky's new playbook",
        "guest": "Brian Chesky",
        "timestamp": "00:00:00",
        "text": "Leaders are in the details."
    }]
    prompt = build_ship30_prompt("How should a founder run roadmap?", chunks)
    assert "Ship 30 for 30" in prompt
    assert "The Hook" in prompt
    assert "short paragraphs" in prompt
    assert "Brian Chesky" in prompt
    assert "[S1]" in prompt
    assert "Leaders are in the details" in prompt
    assert "<artifact" in prompt


def test_ship30_prompt_supports_retriever_fields():
    chunks = [{
        "episode": "Test Episode",
        "guest": "Test Guest",
        "timestamp": "00:01:00",
        "text": "Test transcript evidence."
    }]
    prompt = build_ship30_prompt("Test question", chunks)
    assert "[S1]" in prompt
    assert "Episode: Test Episode" in prompt
    assert "Guest: Test Guest" in prompt
    assert "Test transcript evidence." in prompt


def test_ship30_prompt_empty_context():
    prompt = build_ship30_prompt("Unknown topic", [])
    assert "No relevant transcript chunks" in prompt
    assert "INSUFFICIENT_CONTEXT_REFUSAL" in prompt


def test_grounded_chat_empty_context():
    prompt = build_grounded_system_prompt([])
    assert "NO RELEVANT TRANSCRIPT EVIDENCE WAS FOUND" in prompt


def test_grounded_prompt_contains_source():
    chunks = [{
        "episode": "Brian Chesky's new playbook",
        "guest": "Brian Chesky",
        "timestamp": "00:02:17",
        "text": "Brian discussed product development."
    }]
    prompt = build_grounded_system_prompt(chunks)
    assert "[S1]" in prompt
    assert "Brian Chesky" in prompt
    assert "Brian discussed product development." in prompt


def test_html_artifact_extraction():
    text = """
<artifact identifier="growth-calc" type="html" title="Growth Calculator">
<div>Calculator</div>
</artifact>
"""
    artifacts = extract_artifacts(text)
    assert len(artifacts) == 1
    assert artifacts[0]["identifier"] == "growth-calc"
    assert artifacts[0]["artifact_type"] == "html"
    assert artifacts[0]["title"] == "Growth Calculator"
    assert artifacts[0]["content"] == "<div>Calculator</div>"


def test_markdown_artifact_extraction():
    text = """
<artifact identifier="ship30-essay" type="markdown" title="Product Essay">
## Product Leadership
Useful insight.
</artifact>
"""
    artifacts = extract_artifacts(text)
    assert len(artifacts) == 1
    assert artifacts[0]["identifier"] == "ship30-essay"
    assert artifacts[0]["artifact_type"] == "markdown"
    assert "Product Leadership" in artifacts[0]["content"]


def test_fenced_html_artifact_extraction():
    text = """
```html
<div>
<h1>Growth Calculator</h1>
</div>
```
"""
    artifacts = extract_artifacts(text)
    assert len(artifacts) == 1
    assert artifacts[0]["artifact_type"] == "html"
    assert "Growth Calculator" in artifacts[0]["content"]
