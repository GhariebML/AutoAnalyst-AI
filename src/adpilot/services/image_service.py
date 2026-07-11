import logging
from typing import Dict, Optional
from openai import AsyncOpenAI
from ..core.config import get_config

logger = logging.getLogger(__name__)


class ImageService:
    """Async client for image generation APIs (DALL·E 3)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_config().openai_api_key
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_image(
        self, prompt: str, *, size: str = "1024x1024", quality: str = "standard", **kwargs
    ) -> Optional[Dict[str, str]]:
        """Generate an image using OpenAI DALL·E 3.

        Args:
            prompt: The text prompt for generation.
            size: Image dimensions (default 1024x1024).
            quality: Generation quality (standard or hd).

        Returns:
            Dict containing 'url' and 'revised_prompt', or None if failed.
        """
        if not self.api_key:
            logger.error("OpenAI API key missing for ImageService")
            return None

        try:
            logger.info(f"Generating image with DALL·E 3. Prompt: {prompt[:50]}...")
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )

            image_data = response.data[0]
            return {"url": image_data.url, "revised_prompt": image_data.revised_prompt or prompt}
        except Exception as e:
            logger.error(f"DALL·E 3 generation failed: {str(e)}")
            return None
