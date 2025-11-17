from typing import Dict, List, Optional

from app.services.ai.base import AIExecutor, AIProvider


class FlashcardGenerationService:
    def __init__(self, executor: AIExecutor) -> None:
        self.executor = executor

    async def generate(
        self,
        text_content: str,
        num_cards: int = 10,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        text = text_content[:3000] + "..." if len(text_content) > 3000 else text_content
        prompt = self._build_flashcard_prompt(text, num_cards)

        try:
            response, provider_name, model_name = await self.executor.request(
                prompt, preferred_provider
            )
            flashcards = self._parse_flashcard_response(response)
            return {
                "success": True,
                "flashcards": flashcards,
                "ai_provider": provider_name,
                "ai_model": model_name,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc), "flashcards": []}

    @staticmethod
    def _build_flashcard_prompt(text: str, num_cards: int) -> str:
        return f"""Extract {num_cards} important vocabulary words/phrases from the following text and create flashcards.

Text: {text}

Format each flashcard as:
Front: [Word/Phrase - use **bold** for emphasis]
Back: [Definition - use **bold** for key terms, *italic* for examples]
Example: [Example sentence]

Flashcards:"""

    @staticmethod
    def _parse_flashcard_response(response: str) -> List[Dict]:
        flashcards: List[Dict] = []
        if not response:
            return flashcards

        sections = response.split("Front:")[1:]
        for section in sections:
            if "Back:" not in section:
                continue
            parts = section.split("Back:")
            front = parts[0].strip("* \n")
            remainder = parts[1]
            if "Example:" in remainder:
                back_text, example_text = remainder.split("Example:", 1)
            else:
                back_text, example_text = remainder, ""

            flashcards.append(
                {
                    "front_text": front.strip(),
                    "back_text": back_text.strip(),
                    "example_sentence": example_text.strip(),
                }
            )
        return flashcards

