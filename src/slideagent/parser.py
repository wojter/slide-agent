import logging
import re
from pathlib import Path

from slideagent.models import ParseResult, PresentationMeta, SlideData

logger = logging.getLogger(__name__)

SLIDE_SEPARATOR = "---"
NOTES_HEADER = "## Notes"
META_PATTERNS = {
    "description": re.compile(r"\*\*Description:\*\*\s*(.+)", re.IGNORECASE),
    "keywords": re.compile(r"\*\*Słowa kluczowe:\*\*\s*(.+)", re.IGNORECASE),
    "visual_theme": re.compile(r"\*\*Motyw wizualny:\*\*\s*(.+)", re.IGNORECASE),
}
TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def parse_presentation(path: Path) -> ParseResult:
    """Parse a Markdown presentation file into metadata and slides."""
    _validate_file(path)
    text = path.read_text(encoding="utf-8")
    _validate_content(text, path)

    raw_blocks = _split_into_blocks(text)
    meta = _extract_meta(raw_blocks[0])
    slides = [_parse_slide(block, index) for index, block in enumerate(raw_blocks)]

    logger.info("Parsed %d slides from %s", len(slides), path.name)
    return ParseResult(meta=meta, slides=slides)


def _validate_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")


def _validate_content(text: str, path: Path) -> None:
    if not text.strip():
        raise ValueError(f"Empty input file: {path}")
    if SLIDE_SEPARATOR not in text:
        logger.warning("No slide separators found in %s, treating as single slide", path.name)


def _split_into_blocks(text: str) -> list[str]:
    """Split presentation text by `---` separators into raw blocks."""
    blocks = re.split(r"^\s*---\s*$", text, flags=re.MULTILINE)
    return [block.strip() for block in blocks if block.strip()]


def _extract_meta(first_block: str) -> PresentationMeta:
    """Extract presentation metadata from the first block header."""
    title_match = TITLE_PATTERN.search(first_block)
    title = title_match.group(1).strip() if title_match else ""

    meta = PresentationMeta(title=title)

    for field_name, pattern in META_PATTERNS.items():
        match = pattern.search(first_block)
        if not match:
            continue
        value = match.group(1).strip()
        if field_name == "keywords":
            meta.keywords = [kw.strip() for kw in value.split(",") if kw.strip()]
        else:
            setattr(meta, field_name, value)

    return meta


def _parse_slide(block: str, index: int) -> SlideData:
    """Parse a single slide block into structured SlideData."""
    notes_part, content_part = _split_notes(block)
    title = _extract_slide_title(content_part)
    content = _extract_content(content_part, title)

    return SlideData(
        index=index,
        title=title,
        content=content.strip(),
        notes=notes_part.strip(),
        raw_markdown=block,
    )


def _split_notes(block: str) -> tuple[str, str]:
    """Split block into (notes, everything_else). Returns (notes, rest)."""
    parts = re.split(r"^##\s+Notes\s*$", block, maxsplit=1, flags=re.MULTILINE)
    if len(parts) < 2:
        return "", block

    before_notes = parts[0]
    notes_text = parts[1]

    next_heading = re.search(r"^##\s+(?!Notes)", notes_text, flags=re.MULTILINE)
    if next_heading:
        notes_only = notes_text[: next_heading.start()]
        rest_after = notes_text[next_heading.start() :]
        return notes_only, before_notes + rest_after

    return notes_text, before_notes


def _extract_slide_title(content: str) -> str:
    """Find the first `## heading` that is not `## Notes`."""
    match = re.search(r"^##\s+(?!Notes\b)(.+)$", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_content(content: str, title: str) -> str:
    """Extract slide body: everything except the title line and metadata headers."""
    lines = content.splitlines()
    result_lines: list[str] = []

    title_found = False
    for line in lines:
        stripped = line.strip()

        title_re = r"^##\s+" + re.escape(title) + r"\s*$"
        if not title_found and title and re.match(title_re, stripped):
            title_found = True
            continue

        if TITLE_PATTERN.match(stripped):
            continue
        if any(p.match(stripped) for p in META_PATTERNS.values()):
            continue

        result_lines.append(line)

    return "\n".join(result_lines).strip()
