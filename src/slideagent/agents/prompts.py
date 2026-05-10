import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts"


@dataclass(frozen=True)
class PromptConfig:
    """Parsed prompt file: YAML frontmatter config + Markdown template body."""

    template: str
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024
    response_format: str | None = None
    extra: dict = field(default_factory=dict)

    def render(self, **kwargs: str) -> str:
        """Render the template with the given variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as exc:
            raise ValueError(
                f"Missing template variable {exc} — "
                f"available: {list(kwargs.keys())}"
            ) from exc


def load_prompt(name: str, *, prompts_dir: Path | None = None) -> PromptConfig:
    """Load a prompt file with YAML frontmatter and return a PromptConfig."""
    directory = prompts_dir or PROMPTS_DIR
    path = directory / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    raw = path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(raw)

    return PromptConfig(
        template=body.strip(),
        model=frontmatter.get("model", ""),
        temperature=float(frontmatter.get("temperature", 0.7)),
        max_tokens=int(frontmatter.get("max_tokens", 1024)),
        response_format=frontmatter.get("response_format"),
        extra={k: v for k, v in frontmatter.items()
               if k not in {"model", "temperature", "max_tokens", "response_format"}},
    )


def load_fragment(name: str, *, prompts_dir: Path | None = None) -> str:
    """Load a prompt fragment file (no frontmatter, just plain text)."""
    directory = prompts_dir or PROMPTS_DIR
    path = directory / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt fragment not found: {path}")

    return path.read_text(encoding="utf-8").strip()


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Split a file into YAML frontmatter dict and body text."""
    if not raw.startswith("---"):
        return {}, raw

    parts = raw.split("---", maxsplit=2)
    if len(parts) < 3:
        return {}, raw

    yaml_block = parts[1].strip()
    body = parts[2]

    frontmatter: dict = {}
    for line in yaml_block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip()

    return frontmatter, body
