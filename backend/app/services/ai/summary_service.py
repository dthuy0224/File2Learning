from typing import Dict, Optional

from app.services.ai.base import AIExecutor, AIProvider


class SummaryService:
    def __init__(self, executor: AIExecutor) -> None:
        self.executor = executor

    async def generate(
        self,
        text_content: str,
        max_length: int = 300,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        text = text_content[:6000] + "..." if len(text_content) > 6000 else text_content
        prompt = f"""Please provide a concise summary of the following text in {max_length} words or less:

{text}

Summary:"""

        try:
            response, provider_name, model_name = await self.executor.request(
                prompt, preferred_provider
            )
            return {
                "success": True,
                "summary": response.strip(),
                "ai_provider": provider_name,
                "ai_model": model_name,
                "original_length": len(text_content),
                "summary_length": len(response),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc), "summary": ""}

