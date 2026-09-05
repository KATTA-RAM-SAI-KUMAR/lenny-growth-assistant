import re
from typing import List, Dict


ARTIFACT_REGEX = re.compile(
    r'<artifact\s+identifier="([^"]+)"\s+type="([^"]+)"\s+title="([^"]+)">'
    r'([\s\S]*?)</artifact>',
    re.IGNORECASE
)


def extract_artifacts(text: str) -> List[Dict[str, str]]:
    """
    Extract generated artifacts from the assistant response.

    Supported formats:
    1. Explicit <artifact> blocks.
    2. Fenced HTML blocks.
    3. Fenced Markdown blocks.
    """

    artifacts: List[Dict[str, str]] = []

    # Format 1: Explicit artifact block
    for match in ARTIFACT_REGEX.finditer(text):
        identifier, artifact_type, title, content = match.groups()

        artifacts.append({
            "identifier": identifier.strip(),
            "artifact_type": artifact_type.strip().lower(),
            "title": title.strip(),
            "content": content.strip(),
        })

    if artifacts:
        return artifacts

    # Format 2: Fenced HTML
    html_matches = re.findall(
        r"```html\s*([\s\S]*?)```",
        text,
        re.IGNORECASE
    )

    for index, content in enumerate(html_matches, 1):
        artifacts.append({
            "identifier": f"html-artifact-{index}",
            "artifact_type": "html",
            "title": f"Generated HTML Artifact {index}",
            "content": content.strip(),
        })

    if artifacts:
        return artifacts

    # Format 3: Fenced Markdown
    markdown_matches = re.findall(
        r"```markdown\s*([\s\S]*?)```",
        text,
        re.IGNORECASE
    )

    for index, content in enumerate(markdown_matches, 1):
        artifacts.append({
            "identifier": f"markdown-artifact-{index}",
            "artifact_type": "markdown",
            "title": f"Generated Markdown Artifact {index}",
            "content": content.strip(),
        })

    return artifacts


def remove_artifact_tags(text: str) -> str:
    """Remove explicit artifact blocks from chat display text."""
    return ARTIFACT_REGEX.sub("", text).strip()