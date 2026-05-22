"""LLM service for AI operations."""
import json
import hashlib
from typing import Optional, List, AsyncGenerator

from openai import AsyncOpenAI
import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


class LLMService:
    """Service for LLM interactions with caching."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self._redis: Optional[redis.Redis] = None

    async def get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    def _cache_key(self, prompt: str, system: str = "") -> str:
        content = f"{system}:{prompt}"
        return f"llm_cache:{hashlib.sha256(content.encode()).hexdigest()}"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        use_cache: bool = True,
        json_mode: bool = False
    ) -> str:
        """Generate a response from LLM with optional caching."""
        # Check cache
        if use_cache:
            try:
                r = await self.get_redis()
                cache_key = self._cache_key(prompt, system_prompt)
                cached = await r.get(cache_key)
                if cached:
                    return cached
            except Exception:
                pass  # Redis unavailable, continue without cache

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        result = response.choices[0].message.content

        # Cache result
        if use_cache:
            try:
                r = await self.get_redis()
                cache_key = self._cache_key(prompt, system_prompt)
                await r.setex(cache_key, 3600, result)  # 1 hour TTL
            except Exception:
                pass

        return result

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Stream response from LLM."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> dict:
        """Generate a JSON response from LLM."""
        result = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True
        )
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            start = result.find("{")
            end = result.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(result[start:end])
            raise ValueError(f"Failed to parse LLM response as JSON: {result[:200]}")


# Singleton
llm_service = LLMService()
