import os
import json
import httpx
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaService:
    """Service to interact with Ollama API for AI-powered content generation"""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.client = httpx.Client(timeout=300.0)  # 5 minute timeout for AI generation
        self.default_model = "llama2:7b"

    async def generate_quiz(self, text_content: str, quiz_type: str = "mixed", num_questions: int = 5) -> Dict:
        """
        Generate quiz questions from text content using Ollama

        Args:
            text_content: The document text to generate quiz from
            quiz_type: Type of quiz ("mcq", "fill_blank", "mixed")
            num_questions: Number of questions to generate

        Returns:
            Dict containing quiz questions and metadata
        """
        try:
            max_length = 4000  # Safe limit for llama2:7b
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "..."

            prompt = self._build_quiz_prompt(text_content, quiz_type, num_questions)

            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                }
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

            result = response.json()
            generated_text = result.get("response", "")

            # Parse the generated text to extract quiz questions
            quiz_data = self._parse_quiz_response(generated_text, quiz_type)

            return {
                "success": True,
                "quiz": quiz_data,
                "model_used": self.default_model,
                "text_length": len(text_content)
            }

        except Exception as e:
            logger.error(f"Error generating quiz with Ollama: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._generate_fallback_quiz(text_content, quiz_type, num_questions)
            }

    async def generate_flashcards(self, text_content: str, num_cards: int = 10) -> Dict:
        """
        Generate flashcards from text content
        """
        try:
            max_length = 3000
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "..."

            prompt = self._build_flashcard_prompt(text_content, num_cards)

            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "top_p": 0.8
                    }
                }
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")

            result = response.json()
            generated_text = result.get("response", "")

            flashcards = self._parse_flashcard_response(generated_text)

            return {
                "success": True,
                "flashcards": flashcards,
                "model_used": self.default_model
            }

        except Exception as e:
            logger.error(f"Error generating flashcards with Ollama: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "flashcards": []
            }

    async def generate_summary(self, text_content: str, max_length: int = 300) -> Dict:
        """
        Generate summary of text content
        """
        try:
            # For summary, we can use longer text
            max_input_length = 6000
            if len(text_content) > max_input_length:
                text_content = text_content[:max_input_length] + "..."

            prompt = f"""
            Please provide a concise summary of the following text in {max_length} words or less:

            {text_content}

            Summary:
            """

            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8
                    }
                }
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")

            result = response.json()
            summary = result.get("response", "").strip()

            return {
                "success": True,
                "summary": summary,
                "original_length": len(text_content),
                "summary_length": len(summary)
            }

        except Exception as e:
            logger.error(f"Error generating summary with Ollama: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "summary": ""
            }

    def _build_quiz_prompt(self, text: str, quiz_type: str, num_questions: int) -> str:
        """Build prompt for quiz generation"""
        if quiz_type == "mcq":
            return f"""
            Generate {num_questions} multiple choice questions from the following text:

            Text: {text}

            Format each question as:
            Q: [Question]
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            Correct: [Letter]

            Questions:
            """
        elif quiz_type == "fill_blank":
            return f"""
            Generate {num_questions} fill-in-the-blank questions from the following text:

            Text: {text}

            Format each question as:
            Q: [Question with _____ for blanks]
            A: [Answer]

            Questions:
            """
        else:  # mixed
            return f"""
            Generate {num_questions} mixed quiz questions (MCQ and fill-in-the-blank) from the following text:

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

            Questions:
            """

    def _build_flashcard_prompt(self, text: str, num_cards: int) -> str:
        """Build prompt for flashcard generation"""
        return f"""
        Extract {num_cards} important vocabulary words/phrases from the following text and create flashcards:

        Text: {text}

        Format each flashcard as:
        Front: [Word/Phrase]
        Back: [Definition]
        Example: [Example sentence]

        Flashcards:
        """

    def _parse_quiz_response(self, response: str, quiz_type: str) -> List[Dict]:
        """Parse AI response into structured quiz data"""
        questions = []

        try:
            # Simple parsing - in production, use more robust parsing
            lines = response.strip().split('\n')

            current_question = {}
            for line in lines:
                line = line.strip()
                if line.startswith('Q:'):
                    if current_question:
                        questions.append(current_question)
                    current_question = {'question': line[3:].strip()}
                elif line.startswith(('A)', 'B)', 'C)', 'D)')) and 'question' in current_question:
                    if 'options' not in current_question:
                        current_question['options'] = []
                    current_question['options'].append(line[3:].strip())
                elif line.startswith('Correct:') and 'question' in current_question:
                    current_question['correct_answer'] = line[8:].strip()
                    current_question['question_type'] = 'multiple_choice'
                elif line.startswith('A:') and 'question' in current_question:
                    # This is a fill-in-the-blank answer
                    current_question['correct_answer'] = line[3:].strip()
                    current_question['question_type'] = 'fill_blank'

            if current_question:
                questions.append(current_question)

        except Exception as e:
            logger.error(f"Error parsing quiz response: {str(e)}")

        return questions

    def _parse_flashcard_response(self, response: str) -> List[Dict]:
        """Parse AI response into structured flashcard data"""
        flashcards = []

        try:
            # Simple parsing
            sections = response.split('Front:')[1:]
            for section in sections:
                if 'Back:' in section:
                    parts = section.split('Back:')
                    front = parts[0].strip()

                    if 'Example:' in parts[1]:
                        back_parts = parts[1].split('Example:')
                        back = back_parts[0].strip()
                        example = back_parts[1].strip()
                    else:
                        back = parts[1].strip()
                        example = ""

                    flashcards.append({
                        'front_text': front,
                        'back_text': back,
                        'example_sentence': example
                    })

        except Exception as e:
            logger.error(f"Error parsing flashcard response: {str(e)}")

        return flashcards

    def _generate_fallback_quiz(self, text: str, quiz_type: str, num_questions: int) -> List[Dict]:
        """Generate simple fallback quiz when AI fails"""
        # Simple keyword-based fallback
        words = text.split()[:50]  # First 50 words
        questions = []

        for i in range(min(num_questions, len(words) // 3)):
            word = words[i * 3]
            questions.append({
                'question': f'What does "{word}" mean in this context?',
                'question_type': 'fill_blank',
                'correct_answer': f'Context-dependent meaning of {word}',
                'options': [] if quiz_type == 'fill_blank' else [word, 'Unknown', 'Context', 'Definition']
            })

        return questions


# Global instance
ollama_service = OllamaService()
