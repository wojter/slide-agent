import base64
import logging

from openai import OpenAI

from slideagent.agents.prompts import load_fragment, load_prompt
from slideagent.models import CriticResponse, SlideData

logger = logging.getLogger(__name__)


class VisualCritic:
    """Evaluates generated images for quality, correctness, and style consistency."""

    def __init__(self, client: OpenAI) -> None:
        self._client = client
        self._system = load_prompt("critic_system.md")
        self._user = load_prompt("critic_user.md")
        self._visual_style = load_fragment("visual_style.md")

    def run(
        self,
        image_data: bytes,
        image_prompt: str,
        slide: SlideData,
    ) -> CriticResponse:
        """Evaluate a generated image and return a pass/fail verdict with feedback."""
        user_text = self._user.render(
            slide_title=slide.title,
            slide_content=slide.content,
            slide_notes=slide.notes,
            image_prompt=image_prompt,
            visual_style=self._visual_style,
        )

        b64_image = base64.b64encode(image_data).decode()

        completion = self._client.chat.completions.parse(
            model=self._system.model,
            messages=[
                {"role": "system", "content": self._system.template},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_image}",
                            },
                        },
                    ],
                },
            ],
            temperature=self._system.temperature,
            max_tokens=self._system.max_tokens,
            response_format=CriticResponse,
        )

        result = completion.choices[0].message.parsed
        if result is None:
            refusal = completion.choices[0].message.refusal or "unknown"
            raise ValueError(
                f"Visual critic refused for slide {slide.index}: {refusal}"
            )

        logger.info("Slide %02d: verdict=%s", slide.index, result.verdict)
        return result
