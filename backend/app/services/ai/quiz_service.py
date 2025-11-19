import json
from typing import Dict, List, Optional

from app.services.ai.base import AIExecutor, AIProvider


class QuizGenerationService:
    def __init__(self, executor: AIExecutor) -> None:
        self.executor = executor

    async def generate(
        self,
        text_content: str,
        quiz_type: str = "mixed",
        num_questions: int = 5,
        preferred_provider: Optional[AIProvider] = None,
    ) -> Dict:
        text = text_content[:4000] + "..." if len(text_content) > 4000 else text_content
        prompt = self._build_quiz_prompt(text, quiz_type, num_questions)

        try:
            response, provider_name, model_name = await self.executor.request(
                prompt, preferred_provider
            )
            questions = self._parse_quiz_response(response)
            if not questions:
                raise ValueError("AI did not return any valid quiz questions")

            return {
                "success": True,
                "quiz": questions,
                "ai_provider": provider_name,
                "ai_model": model_name,
                "text_length": len(text),
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "fallback": self._generate_fallback_quiz(text, quiz_type, num_questions),
            }

    @staticmethod
    def _build_quiz_prompt(text: str, quiz_type: str, num_questions: int) -> str:
        # Map quiz types to consistent format
        if quiz_type == "multiple_choice" or quiz_type == "mcq":
            return f"""Generate {num_questions} multiple choice questions from the following text:

Text: {text}
    
Format each question as:
Q: [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [Letter]

Questions:"""
        if quiz_type == "fill_blank" or quiz_type == "fill_in_the_blank":
            return f"""Generate {num_questions} fill-in-the-blank questions from the following text:

Text: {text}

Format each question as:
Q: [Question with _____ for blanks]
A: [Answer]

Questions:"""
        # Default to mixed if not specified
        return f"""Generate {num_questions} mixed quiz questions (MCQ and fill-in-the-blank) from the following text:

Text: {text}

Format MCQ as:
Q: [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [Letter]

Format fill-in-the-blank as:
Q: [Question with _____]
A: [Answer]

Questions:"""

    @staticmethod
    def _parse_quiz_response(response: str) -> List[Dict]:
        questions: List[Dict] = []
        current_question: Dict[str, any] = {}

        for raw_line in response.strip().split("\n"):
            line = raw_line.strip()
            if line.startswith("Q:"):
                if current_question:
                    questions.append(current_question)
                current_question = {"question": line[3:].strip()}
            elif line.startswith(("A)", "B)", "C)", "D)")) and current_question:
                current_question.setdefault("options", []).append(line[3:].strip())
            elif line.startswith("Correct:") and current_question:
                current_question["correct_answer"] = line[8:].strip()
                current_question["question_type"] = "multiple_choice"
            elif line.startswith("A:") and current_question:
                current_question["correct_answer"] = line[3:].strip()
                current_question["question_type"] = "fill_blank"

        if current_question:
            questions.append(current_question)
        return [q for q in questions if q.get("question") and q.get("correct_answer")]

    @staticmethod
    def _generate_fallback_quiz(text: str, quiz_type: str, num_questions: int) -> List[Dict]:
        words = text.split()[:50]
        questions: List[Dict] = []
        for i in range(min(num_questions, max(len(words) // 3, 1))):
            word = words[i * 3]
            questions.append(
                {
                    "question": f'What does "{word}" mean in this context?',
                    "question_type": quiz_type if quiz_type in {"fill_blank", "mcq"} else "fill_blank",
                    "correct_answer": f"Meaning of {word} based on the passage",
                    "options": [] if quiz_type == "fill_blank" else [word, "Definition", "Context", "Usage"],
                }
            )
        return questions

