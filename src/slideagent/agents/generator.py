import logging

from openai import OpenAI

from slideagent.agents.prompts import load_fragment, load_prompt
from slideagent.models import PresentationMeta, SlideData, SlideDecision

logger = logging.getLogger(__name__)


class GenerationAgent:
    """Decides skip/generate per slide and creates an image prompt."""

    def __init__(self, client: OpenAI) -> None:
        self._client = client
        self._system = load_prompt("generation_system.md")
        self._user = load_prompt("generation_user.md")
        self._visual_style = load_fragment("visual_style.md")
        self._retry_template = load_fragment("retry_context.md")

    def run(
        self,
        slide: SlideData,
        meta: PresentationMeta,
        *,
        attempt_number: int = 1,
        max_attempts: int = 3,
        previous_prompt: str = "",
        feedback: str = "",
    ) -> SlideDecision:
        """Analyze a slide and return a skip/generate decision with an optional image prompt."""
        retry_context = self._build_retry_context(
            attempt_number, max_attempts, previous_prompt, feedback
        )
        user_content = self._render_user_message(slide, meta, retry_context)

        completion = self._client.chat.completions.parse(
            model=self._system.model,
            messages=[
                {"role": "system", "content": self._system.template},
                {"role": "user", "content": user_content},
            ],
            temperature=self._system.temperature,
            max_tokens=self._system.max_tokens,
            response_format=SlideDecision,
        )

        result = completion.choices[0].message.parsed
        if result is None:
            refusal = completion.choices[0].message.refusal or "unknown"
            raise ValueError(
                f"Generation agent refused for slide {slide.index}: {refusal}"
            )

        logger.info(
            "Slide %02d: decision=%s, prompt_len=%d",
            slide.index,
            result.decision,
            len(result.prompt),
        )
        return result

    def _build_retry_context(
        self,
        attempt_number: int,
        max_attempts: int,
        previous_prompt: str,
        feedback: str,
    ) -> str:
        if attempt_number <= 1 or not feedback:
            return ""
        return self._retry_template.format(
            attempt_number=attempt_number,
            max_attempts=max_attempts,
            previous_prompt=previous_prompt,
            feedback=feedback,
        )

    def _render_user_message(
        self,
        slide: SlideData,
        meta: PresentationMeta,
        retry_context: str,
    ) -> str:
        return self._user.render(
            presentation_title=meta.title,
            presentation_description=meta.description,
            presentation_keywords=", ".join(meta.keywords),
            presentation_visual_theme=meta.visual_theme,
            visual_style=self._visual_style,
            slide_index=str(slide.index),
            slide_title=slide.title,
            slide_content=slide.content,
            slide_notes=slide.notes,
            retry_context=retry_context,
        )
