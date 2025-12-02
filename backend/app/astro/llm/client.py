"""
Minimax M2 API Client for StarMeet

This client communicates with MiniMax Text API for generating
personality reports based on pre-calculated astrological data.

API Documentation: https://platform.minimax.io/docs
"""
import os
import time
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MinimaxConfig:
    """Minimax API configuration"""
    api_key: str
    base_url: str = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    model: str = "MiniMax-Text-01"
    temperature: float = 0.7
    max_tokens: int = 8000
    timeout: float = 120.0  # 2 minutes for long reports


class MinimaxAPIError(Exception):
    """Custom exception for Minimax API errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        if self.status_code:
            return f"MinimaxAPIError({self.status_code}): {self.message}"
        return f"MinimaxAPIError: {self.message}"


class MinimaxClient:
    """
    Async client for Minimax M2 API.

    Usage:
        async with MinimaxClient() as client:
            response = await client.generate(system_prompt, user_prompt)

    Or for single calls:
        client = MinimaxClient()
        response = await client.generate(system_prompt, user_prompt)
    """

    def __init__(self, config: Optional[MinimaxConfig] = None):
        """
        Initialize client with config or from environment.

        Args:
            config: Optional MinimaxConfig. If not provided, loads from env.

        Raises:
            ValueError: If MINIMAX_API_KEY is not set
        """
        if config is None:
            api_key = os.getenv("MINIMAX_API_KEY")
            if not api_key:
                raise ValueError(
                    "MINIMAX_API_KEY environment variable not set. "
                    "Set it in .env file or pass config explicitly."
                )
            config = MinimaxConfig(api_key=api_key)

        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Enter async context manager"""
        self._client = httpx.AsyncClient(timeout=self.config.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager"""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers with authorization"""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Minimax M2.

        Args:
            system_prompt: System instructions (role, rules, format)
            user_prompt: User message with formatted data
            temperature: Override default temperature (0.0-1.0)
            max_tokens: Override default max tokens

        Returns:
            Generated text content

        Raises:
            MinimaxAPIError: On API errors or invalid responses
        """
        # Create client if not in context manager
        should_close = False
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
            should_close = True

        try:
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
                "stream": False
            }

            logger.info(
                f"Sending request to Minimax API "
                f"(model: {self.config.model}, "
                f"system_prompt: {len(system_prompt)} chars, "
                f"user_prompt: {len(user_prompt)} chars)"
            )

            start_time = time.time()

            response = await self._client.post(
                self.config.base_url,
                headers=self.headers,
                json=payload
            )

            latency_ms = (time.time() - start_time) * 1000

            # Handle errors
            if response.status_code != 200:
                error_body = {}
                try:
                    error_body = response.json()
                except Exception:
                    pass

                logger.error(
                    f"Minimax API error: {response.status_code} - {error_body}"
                )
                raise MinimaxAPIError(
                    message=f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response=error_body
                )

            data = response.json()

            # Extract content from response
            # Minimax format: {"choices": [{"message": {"content": "..."}}]}
            if "choices" not in data or len(data["choices"]) == 0:
                logger.error(f"Invalid response format: {data}")
                raise MinimaxAPIError(
                    message="Invalid response format: no choices in response",
                    response=data
                )

            content = data["choices"][0].get("message", {}).get("content", "")

            if not content:
                raise MinimaxAPIError(
                    message="Empty content in response",
                    response=data
                )

            logger.info(
                f"Generated {len(content)} chars in {latency_ms:.0f}ms"
            )

            return content

        except httpx.TimeoutException:
            logger.error(f"Request timed out after {self.config.timeout}s")
            raise MinimaxAPIError(
                message=f"Request timed out after {self.config.timeout}s"
            )

        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise MinimaxAPIError(
                message=f"Request failed: {str(e)}"
            )

        finally:
            if should_close and self._client:
                await self._client.aclose()
                self._client = None

    async def generate_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        **kwargs
    ) -> str:
        """
        Generate with automatic retry on failure.

        Uses exponential backoff between retries.

        Args:
            system_prompt: System instructions
            user_prompt: User message
            max_retries: Maximum number of attempts
            retry_delay: Initial delay between retries (seconds)
            **kwargs: Additional args passed to generate()

        Returns:
            Generated text content

        Raises:
            MinimaxAPIError: If all retries fail
        """
        last_error = None
        current_delay = retry_delay

        for attempt in range(max_retries):
            try:
                return await self.generate(system_prompt, user_prompt, **kwargs)

            except MinimaxAPIError as e:
                last_error = e

                # Don't retry on client errors (4xx)
                if e.status_code and 400 <= e.status_code < 500:
                    logger.error(f"Client error, not retrying: {e}")
                    raise

                if attempt < max_retries - 1:
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {e.message}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All {max_retries} attempts failed")

        raise last_error

    async def health_check(self) -> bool:
        """
        Check if API is accessible.

        Returns:
            True if API responds, False otherwise
        """
        try:
            # Send minimal request
            await self.generate(
                system_prompt="Say 'OK'",
                user_prompt="Health check",
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False


# ============================================================================
# Synchronous Wrapper
# ============================================================================

def generate_sync(
    system_prompt: str,
    user_prompt: str,
    **kwargs
) -> str:
    """
    Synchronous wrapper for generate().

    Use in non-async contexts like tests, CLI, or simple scripts.

    Args:
        system_prompt: System instructions
        user_prompt: User message
        **kwargs: Additional args passed to generate()

    Returns:
        Generated text content
    """
    async def _run():
        async with MinimaxClient() as client:
            return await client.generate(system_prompt, user_prompt, **kwargs)

    return asyncio.run(_run())


def generate_with_retry_sync(
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3,
    **kwargs
) -> str:
    """
    Synchronous wrapper for generate_with_retry().
    """
    async def _run():
        async with MinimaxClient() as client:
            return await client.generate_with_retry(
                system_prompt,
                user_prompt,
                max_retries=max_retries,
                **kwargs
            )

    return asyncio.run(_run())
