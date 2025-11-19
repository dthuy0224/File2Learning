import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

from dotenv import find_dotenv, load_dotenv

# Ensure .env is loaded when running locally
_root_env = find_dotenv(filename=".env", usecwd=True)
if _root_env:
    load_dotenv(_root_env)

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    GEMINI = "gemini"
    GROQ = "groq"


class AIExecutor:
    """
    Shared provider bootstrapper and router used by all AI generation services.
    """

    def __init__(self) -> None:
        self.gemini_client = None
        self.groq_client = None
        self.provider_stats: Dict[str, Dict[str, int]] = {
            "gemini": {"success": 0, "failures": 0},
            "groq": {"success": 0, "failures": 0},
        }
        self.provider_cooldowns: Dict[str, datetime] = {}
        self._init_gemini()
        self._init_groq()

    def _init_gemini(self) -> None:
        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash-exp")
                logger.info("✅ Gemini API initialized (FREE tier)")
            else:
                logger.warning(
                    "⚠️ GEMINI_API_KEY not found. Get a free key at https://makersuite.google.com/app/apikey"
                )
        except Exception as exc:  # pragma: no cover - logging only
            logger.error("Failed to initialize Gemini: %s", exc)

    def _init_groq(self) -> None:
        try:
            from groq import Groq

            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.groq_client = Groq(api_key=api_key)
                logger.info("✅ Groq API initialized (FREE tier)")
            else:
                logger.warning(
                    "⚠️ GROQ_API_KEY not found. Get a free key at https://console.groq.com"
                )
        except Exception as exc:  # pragma: no cover - logging only
            logger.error("Failed to initialize Groq: %s", exc)

    async def request(
        self,
        prompt: str,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Tuple[str, str, str]:
        """
        Execute the prompt using the best available provider.
        Returns a tuple of (response_text, provider_name, model_name).
        Raises RuntimeError if all providers fail.
        """
        providers = self._get_provider_order(preferred_provider)

        for provider in providers:
            if not self._is_provider_available(provider):
                continue
            try:
                response = await self._execute_provider(provider, prompt)
                if response:
                    self.provider_stats[provider.value]["success"] += 1
                    return response.strip(), provider.value, self._get_model_name(provider)
            except Exception as exc:  # pragma: no cover - logging only
                logger.error("%s provider failed: %s", provider.value, exc)
                self.provider_stats[provider.value]["failures"] += 1
                self._handle_provider_failure(provider, exc)

        raise RuntimeError("All AI providers unavailable")

    async def _execute_provider(self, provider: AIProvider, prompt: str) -> Optional[str]:
        if provider == AIProvider.GEMINI and self.gemini_client:
            return await self._generate_with_gemini(prompt)
        if provider == AIProvider.GROQ and self.groq_client:
            return await self._generate_with_groq(prompt)
        return None

    async def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        if not self.gemini_client:
            return None
        response = self.gemini_client.generate_content(prompt)
        return response.text

    async def _generate_with_groq(self, prompt: str) -> Optional[str]:
        if not self.groq_client:
            return None
        completion = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for education."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        return completion.choices[0].message.content

    def _get_provider_order(self, preferred: Optional[AIProvider]) -> List[AIProvider]:
        available = [p for p in [AIProvider.GEMINI, AIProvider.GROQ] if self._has_client(p)]
        if preferred and preferred in available:
            order = [preferred]
            order.extend([p for p in available if p != preferred])
            return order
        return available

    @staticmethod
    def _get_model_name(provider: AIProvider) -> str:
        mapping = {
            AIProvider.GEMINI: "gemini-2.0-flash-exp (FREE)",
            AIProvider.GROQ: "llama-3.3-70b-versatile (FREE)",
        }
        return mapping.get(provider, "unknown")

    def get_stats(self) -> Dict[str, Dict[str, int]]:
        return self.provider_stats

    def _has_client(self, provider: AIProvider) -> bool:
        if provider == AIProvider.GEMINI:
            return self.gemini_client is not None
        if provider == AIProvider.GROQ:
            return self.groq_client is not None
        return False

    def _is_provider_available(self, provider: AIProvider) -> bool:
        if not self._has_client(provider):
            return False
        cooldown_until = self.provider_cooldowns.get(provider.value)
        if cooldown_until and cooldown_until > datetime.utcnow():
            return False
        return True

    def _handle_provider_failure(self, provider: AIProvider, exc: Exception) -> None:
        message = str(exc).lower()
        if any(keyword in message for keyword in ("quota", "rate limit", "429")):
            cooldown_seconds = int(os.getenv("AI_PROVIDER_COOLDOWN_SECONDS", "600"))
            self.provider_cooldowns[provider.value] = datetime.utcnow() + timedelta(
                seconds=cooldown_seconds
            )
            logger.warning(
                "%s marked unavailable for %ss due to quota/rate limits",
                provider.value,
                cooldown_seconds,
            )

