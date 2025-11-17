import json
from typing import Dict, List, Optional

from app.services.ai.base import AIExecutor, AIProvider


class VocabularyExtractionService:
    def __init__(self, executor: AIExecutor) -> None:
        self.executor = executor

    async def generate(
        self,
        text_content: str,
        num_terms: int = 8,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        text = text_content[:4000] + "..." if len(text_content) > 4000 else text_content
        prompt = f"""Identify the {num_terms} most important vocabulary words or phrases from the following passage.
Return ONLY a valid JSON array (no markdown). Each item must have:
- "term"
- "definition"
- "example"

Passage:
{text}

JSON:"""

        try:
            response, provider_name, model_name = await self.executor.request(
                prompt, preferred_provider
            )
            vocab_list = self._parse_key_vocabulary_response(response)
            return {
                "success": True,
                "key_vocabulary": vocab_list,
                "ai_provider": provider_name,
                "ai_model": model_name,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc), "key_vocabulary": []}

    @staticmethod
    def _parse_key_vocabulary_response(response: str) -> List[Dict]:
        if not response:
            return []

        cleaned = response.strip()
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]

        vocab_list: List[Dict] = []
        try:
            data = json.loads(cleaned)
            for item in data:
                term = item.get("term") or item.get("word")
                definition = item.get("definition") or item.get("meaning")
                example = item.get("example") or ""
                if term and definition:
                    vocab_list.append(
                        {
                            "term": term.strip(),
                            "definition": definition.strip(),
                            "example": example.strip(),
                        }
                    )
        except json.JSONDecodeError:
            pass
        return vocab_list

