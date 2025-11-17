"""
High-level facade that exposes quiz/flashcard/vocabulary/summary/chat generation using
modular AI services backed by the shared AIExecutor.
"""

from typing import Dict, Optional, List

from app.services.ai.base import AIExecutor, AIProvider
from app.services.ai.chat_service import ChatService
from app.services.ai.flashcard_service import FlashcardGenerationService
from app.services.ai.quiz_service import QuizGenerationService
from app.services.ai.summary_service import SummaryService
from app.services.ai.vocabulary_service import VocabularyExtractionService


class MultiAIService:
    def __init__(self) -> None:
        self.executor = AIExecutor()
        self.quiz_service = QuizGenerationService(self.executor)
        self.flashcard_service = FlashcardGenerationService(self.executor)
        self.vocab_service = VocabularyExtractionService(self.executor)
        self.summary_service = SummaryService(self.executor)
        self.chat_service = ChatService(self.executor)

    async def generate_quiz(
        self,
        text_content: str,
        quiz_type: str = "mixed",
        num_questions: int = 5,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        return await self.quiz_service.generate(
            text_content=text_content,
            quiz_type=quiz_type,
            num_questions=num_questions,
            preferred_provider=preferred_provider,
        )

    async def generate_flashcards(
        self,
        text_content: str,
        num_cards: int = 10,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        return await self.flashcard_service.generate(
            text_content=text_content,
            num_cards=num_cards,
            preferred_provider=preferred_provider,
        )

    async def generate_key_vocabulary(
        self,
        text_content: str,
        num_terms: int = 8,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        return await self.vocab_service.generate(
            text_content=text_content,
            num_terms=num_terms,
            preferred_provider=preferred_provider,
        )

    async def generate_summary(
        self,
        text_content: str,
        max_length: int = 300,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        return await self.summary_service.generate(
            text_content=text_content,
            max_length=max_length,
            preferred_provider=preferred_provider,
        )

    async def generate_chat_response(
        self,
        text_content: str,
        user_query: str,
        chat_history: Optional[List[Dict]] = None,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        return await self.chat_service.generate(
            text_content=text_content,
            user_query=user_query,
            chat_history=chat_history,
            preferred_provider=preferred_provider,
        )

    def get_stats(self) -> Dict:
        return {
            "providers": self.executor.get_stats(),
            "available_providers": {
                "gemini": self.executor.gemini_client is not None,
                "groq": self.executor.groq_client is not None,
            },
        }


multi_ai_service = MultiAIService()

