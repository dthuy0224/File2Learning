from typing import Dict, List, Optional

from app.services.ai.base import AIExecutor, AIProvider


class ChatService:
    def __init__(self, executor: AIExecutor) -> None:
        self.executor = executor

    async def generate(
        self,
        text_content: str,
        user_query: str,
        chat_history: Optional[List[Dict]] = None,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        chat_history = chat_history or []
        text = text_content[:6000] + "..." if len(text_content) > 6000 else text_content
        prompt = self._build_chat_prompt(text, user_query, chat_history)

        try:
            response, provider_name, model_name = await self.executor.request(
                prompt, preferred_provider
            )
            return {
                "success": True,
                "answer": response.strip(),
                "ai_provider": provider_name,
                "ai_model": model_name,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "answer": "Sorry, I am unable to answer your question right now. Please try again later.",
            }

    @staticmethod
    def _build_chat_prompt(
        document_content: str,
        user_query: str,
        conversation_history: List[Dict],
    ) -> str:
        system_prompt = """You are a helpful AI assistant that can answer questions about documents and general topics.
Priority and Rules:
1. FIRST PRIORITY: If the question is related to the provided document, answer STRICTLY based on information available in the document. Be accurate and cite specific details from the document when possible.
2. SECOND PRIORITY: If the question is NOT related to the document, you may answer using your general knowledge, but clearly indicate that your answer is based on general knowledge, not the document.
3. When answering from the document, be precise and accurate. Do not make up information that is not in the document.
4. When answering general questions, be helpful and informative while maintaining accuracy.
5. Keep responses concise, clear, and helpful.
6. Respond in English for better document understanding, but understand Vietnamese user queries.

Document Content:
"""

        prompt = system_prompt + document_content + "\n\n"
        if conversation_history:
            prompt += "Chat History:\n"
            for msg in conversation_history[-5:]:
                role = "User" if msg.get("role") == "user" else "AI"
                content = msg.get("content", "")
                prompt += f"{role}: {content}\n"
        prompt += f"\nUser query: {user_query}\n\nAnswer:"
        return prompt

