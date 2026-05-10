from typing import Protocol


class ImageProvider(Protocol):
    """Abstract interface for image generation providers."""

    def generate(self, prompt: str) -> bytes:
        """Generate an image from a text prompt. Returns raw image bytes (PNG)."""
        ...
