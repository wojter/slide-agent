from enum import StrEnum

from pydantic import BaseModel, Field


class Decision(StrEnum):
    SKIP = "skip"
    GENERATE = "generate"


class CriticVerdict(StrEnum):
    PASS = "pass"
    FAIL = "fail"


class SlideStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    PASSED = "passed"
    FALLBACK = "fallback"
    SKIPPED = "skipped"


class PresentationMeta(BaseModel):
    """Metadata extracted from the Markdown presentation header."""

    title: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    visual_theme: str = ""


class SlideData(BaseModel):
    """A single parsed slide from the Markdown presentation."""

    index: int
    title: str = ""
    content: str = ""
    notes: str = ""
    raw_markdown: str = ""


class ParseResult(BaseModel):
    """Complete result of parsing a Markdown presentation."""

    meta: PresentationMeta
    slides: list[SlideData]


class AttemptResult(BaseModel):
    """Result of a single image generation + critique cycle."""

    attempt_number: int
    prompt: str = ""
    image_data: bytes = b""
    verdict: CriticVerdict | None = None
    feedback: str = ""


class SlideDecision(BaseModel):
    """Generation Agent's decision for a single slide."""

    decision: Decision
    reasoning: str = ""
    prompt: str = ""


class SlideResult(BaseModel):
    """Full pipeline result for a single slide."""

    slide: SlideData
    decision: SlideDecision | None = None
    attempts: list[AttemptResult] = Field(default_factory=list)
    final_image: bytes = b""
    status: SlideStatus = SlideStatus.PENDING
