import base64
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIImageProvider:
    """Image generation using OpenAI's image models (e.g. gpt-image-2)."""

    def __init__(
        self,
        client: OpenAI,
        *,
        model: str = "gpt-image-2",
        size: str = "1024x1024",
        quality: str = "low",
    ) -> None:
        self._client = client
        self._model = model
        self._size = size
        self._quality = quality

    def generate(self, prompt: str) -> bytes:
        """Generate an image and return raw PNG bytes."""
        logger.info("Generating image with %s (%s, %s)", self._model, self._size, self._quality)

        response = self._client.images.generate(
            model=self._model,
            prompt=prompt,
            n=1,
            size=self._size,
            quality=self._quality,
            response_format="b64_json",
        )

        b64 = response.data[0].b64_json
        if not b64:
            raise RuntimeError(f"Image generation returned empty data for model {self._model}")

        return base64.b64decode(b64)
