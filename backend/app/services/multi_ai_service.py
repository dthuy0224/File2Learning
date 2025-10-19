"""
Multi-Provider AI Service
Supports: Gemini (primary), Groq (backup), Ollama (fallback)
All FREE options optimized for students!
"""

import os
import json
import logging
from typing import Dict, List, Optional, Literal
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Available AI providers"""
    GEMINI = "gemini"
    GROQ = "groq"
    OLLAMA = "ollama"


class MultiAIService:
    """
    Smart AI service that routes requests to multiple FREE providers
    Priority: Gemini (FREE 1500/day) -> Groq (FREE 14400/day) -> Ollama (local)
    """

    def __init__(self):
        self.gemini_client = None
        self.groq_client = None
        self.ollama_base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Initialize providers
        self._init_gemini()
        self._init_groq()
        
        # Track usage for smart routing
        self.provider_stats = {
            "gemini": {"success": 0, "failures": 0},
            "groq": {"success": 0, "failures": 0},
            "ollama": {"success": 0, "failures": 0}
        }

    def _init_gemini(self):
        """Initialize Google Gemini API (FREE)"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # Use gemini-2.0-flash-exp (latest free model as of 2025)
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✅ Gemini API initialized (FREE tier)")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not found. Get free key at: https://makersuite.google.com/app/apikey")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    def _init_groq(self):
        """Initialize Groq API (FREE, super fast)"""
        try:
            from groq import Groq
            
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.groq_client = Groq(api_key=api_key)
                logger.info("✅ Groq API initialized (FREE tier, super fast)")
            else:
                logger.warning("⚠️ GROQ_API_KEY not found. Get free key at: https://console.groq.com")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {str(e)}")

    async def generate_quiz(
        self, 
        text_content: str, 
        quiz_type: str = "mixed", 
        num_questions: int = 5,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict:
        """
        Generate quiz questions using best available AI provider
        """
        max_length = 4000
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "..."

        prompt = self._build_quiz_prompt(text_content, quiz_type, num_questions)
        
        # Try providers in order: Gemini -> Groq -> Ollama
        providers = self._get_provider_order(preferred_provider)
        
        for provider in providers:
            try:
                logger.info(f"🤖 Attempting quiz generation with {provider.value}")
                
                if provider == AIProvider.GEMINI and self.gemini_client:
                    result = await self._generate_with_gemini(prompt)
                elif provider == AIProvider.GROQ and self.groq_client:
                    result = await self._generate_with_groq(prompt)
                else:  # Ollama fallback
                    result = await self._generate_with_ollama(prompt)
                
                if result:
                    questions = self._parse_quiz_response(result, quiz_type)
                    self.provider_stats[provider.value]["success"] += 1
                    
                    return {
                        "success": True,
                        "quiz": questions,
                        "ai_provider": provider.value,
                        "ai_model": self._get_model_name(provider),
                        "text_length": len(text_content)
                    }
                    
            except Exception as e:
                logger.error(f"❌ {provider.value} failed: {str(e)}")
                self.provider_stats[provider.value]["failures"] += 1
                continue
        
        # All providers failed - return fallback
        logger.error("All AI providers failed, using fallback")
        return {
            "success": False,
            "error": "All AI providers unavailable",
            "fallback": self._generate_fallback_quiz(text_content, quiz_type, num_questions)
        }

    async def generate_flashcards(
        self, 
        text_content: str, 
        num_cards: int = 10,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict:
        """
        Generate flashcards using best available AI provider
        """
        max_length = 3000
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "..."

        prompt = self._build_flashcard_prompt(text_content, num_cards)
        providers = self._get_provider_order(preferred_provider)
        
        for provider in providers:
            try:
                logger.info(f"🤖 Attempting flashcard generation with {provider.value}")
                
                if provider == AIProvider.GEMINI and self.gemini_client:
                    result = await self._generate_with_gemini(prompt)
                elif provider == AIProvider.GROQ and self.groq_client:
                    result = await self._generate_with_groq(prompt)
                else:
                    result = await self._generate_with_ollama(prompt)
                
                if result:
                    flashcards = self._parse_flashcard_response(result)
                    self.provider_stats[provider.value]["success"] += 1
                    
                    return {
                        "success": True,
                        "flashcards": flashcards,
                        "ai_provider": provider.value,
                        "ai_model": self._get_model_name(provider)
                    }
                    
            except Exception as e:
                logger.error(f"❌ {provider.value} failed: {str(e)}")
                self.provider_stats[provider.value]["failures"] += 1
                continue
        
        return {
            "success": False,
            "error": "All AI providers unavailable",
            "flashcards": []
        }

    async def generate_summary(
        self, 
        text_content: str, 
        max_length: int = 300,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict:
        """
        Generate summary using best available AI provider
        """
        max_input_length = 6000
        if len(text_content) > max_input_length:
            text_content = text_content[:max_input_length] + "..."

        prompt = f"""Please provide a concise summary of the following text in {max_length} words or less:

{text_content}

Summary:"""

        providers = self._get_provider_order(preferred_provider)
        
        for provider in providers:
            try:
                logger.info(f"🤖 Attempting summary generation with {provider.value}")
                
                if provider == AIProvider.GEMINI and self.gemini_client:
                    result = await self._generate_with_gemini(prompt)
                elif provider == AIProvider.GROQ and self.groq_client:
                    result = await self._generate_with_groq(prompt)
                else:
                    result = await self._generate_with_ollama(prompt)
                
                if result:
                    self.provider_stats[provider.value]["success"] += 1
                    
                    return {
                        "success": True,
                        "summary": result.strip(),
                        "ai_provider": provider.value,
                        "ai_model": self._get_model_name(provider),
                        "original_length": len(text_content),
                        "summary_length": len(result)
                    }
                    
            except Exception as e:
                logger.error(f"❌ {provider.value} failed: {str(e)}")
                self.provider_stats[provider.value]["failures"] += 1
                continue
        
        return {
            "success": False,
            "error": "All AI providers unavailable",
            "summary": ""
        }

    async def generate_chat_response(
        self, 
        text_content: str, 
        user_query: str, 
        chat_history: Optional[List[Dict]] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict:
        """
        Generate chat response using best available AI provider
        """
        if chat_history is None:
            chat_history = []

        max_input_length = 6000
        if len(text_content) > max_input_length:
            text_content = text_content[:max_input_length] + "..."

        prompt = self._build_chat_prompt(text_content, user_query, chat_history)
        providers = self._get_provider_order(preferred_provider)
        
        for provider in providers:
            try:
                logger.info(f"🤖 Attempting chat response with {provider.value}")
                
                if provider == AIProvider.GEMINI and self.gemini_client:
                    result = await self._generate_with_gemini(prompt)
                elif provider == AIProvider.GROQ and self.groq_client:
                    result = await self._generate_with_groq(prompt)
                else:
                    result = await self._generate_with_ollama(prompt)
                
                if result:
                    self.provider_stats[provider.value]["success"] += 1
                    
                    return {
                        "success": True,
                        "answer": result.strip(),
                        "ai_provider": provider.value,
                        "ai_model": self._get_model_name(provider)
                    }
                    
            except Exception as e:
                logger.error(f"❌ {provider.value} failed: {str(e)}")
                self.provider_stats[provider.value]["failures"] += 1
                continue
        
        return {
            "success": False,
            "error": "All AI providers unavailable",
            "answer": "Sorry, I am unable to answer your question right now. Please try again later."
        }

    async def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Generate response using Google Gemini (FREE)"""
        if not self.gemini_client:
            return None
        
        try:
            response = self.gemini_client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return None

    async def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """Generate response using Groq (FREE, super fast)"""
        if not self.groq_client:
            return None
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Latest Groq model (2025)
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for education."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq error: {str(e)}")
            return None

    async def _generate_with_ollama(self, prompt: str) -> Optional[str]:
        """Generate response using local Ollama (always available fallback)"""
        try:
            import httpx
            
            client = httpx.Client(timeout=300.0)
            response = client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": "phi3:mini",  # Lightweight model
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            return None
            
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}")
            return None

    def _get_provider_order(self, preferred: Optional[AIProvider] = None) -> List[AIProvider]:
        """
        Get provider priority order
        Default: Gemini -> Groq -> Ollama
        """
        if preferred:
            # Put preferred provider first
            order = [preferred]
            for p in [AIProvider.GEMINI, AIProvider.GROQ, AIProvider.OLLAMA]:
                if p != preferred:
                    order.append(p)
            return order
        
        # Default order: fastest FREE options first
        return [AIProvider.GEMINI, AIProvider.GROQ, AIProvider.OLLAMA]

    def _get_model_name(self, provider: AIProvider) -> str:
        """Get model name for provider"""
        models = {
            AIProvider.GEMINI: "gemini-2.0-flash-exp (FREE)",
            AIProvider.GROQ: "llama-3.3-70b-versatile (FREE)",
            AIProvider.OLLAMA: "phi3:mini (local)"
        }
        return models.get(provider, "unknown")

    def _build_quiz_prompt(self, text: str, quiz_type: str, num_questions: int) -> str:
        """Build prompt for quiz generation"""
        if quiz_type == "mcq":
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
        elif quiz_type == "fill_blank":
            return f"""Generate {num_questions} fill-in-the-blank questions from the following text:

Text: {text}

Format each question as:
Q: [Question with _____ for blanks]
A: [Answer]

Questions:"""
        else:  # mixed
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

    def _build_flashcard_prompt(self, text: str, num_cards: int) -> str:
        """Build prompt for flashcard generation"""
        return f"""Extract {num_cards} important vocabulary words/phrases from the following text and create flashcards:

Text: {text}

Format each flashcard as:
Front: [Word/Phrase]
Back: [Definition]
Example: [Example sentence]

Flashcards:"""

    def _build_chat_prompt(self, document_content: str, user_query: str, conversation_history: List[Dict]) -> str:
        """Build prompt for chat response"""
        system_prompt = """You are a helpful AI assistant specialized in answering questions based on provided document content.

Rules:
1. Answer only based on information available in the provided document
2. If the question is not related to the document, politely decline to answer
3. Keep responses concise, clear, and helpful
4. Respond in English for better document understanding, but understand Vietnamese user queries

Document:
"""
        
        full_prompt = system_prompt + document_content
        
        if conversation_history:
            full_prompt += "\n\nChat History:\n"
            for msg in conversation_history[-5:]:
                role = "User" if msg.get("role") == "user" else "AI"
                content = msg.get("content", "")
                full_prompt += f"{role}: {content}\n"
        
        full_prompt += f"\nUser query: {user_query}\n\nAnswer:"
        
        return full_prompt

    def _parse_quiz_response(self, response: str, quiz_type: str) -> List[Dict]:
        """Parse AI response into structured quiz data"""
        questions = []
        
        try:
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
        """Generate simple fallback quiz when all AI providers fail"""
        words = text.split()[:50]
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

    def get_stats(self) -> Dict:
        """Get usage statistics for all providers"""
        return {
            "providers": self.provider_stats,
            "available_providers": {
                "gemini": self.gemini_client is not None,
                "groq": self.groq_client is not None,
                "ollama": True  # Always available as fallback
            }
        }


# Global instance
multi_ai_service = MultiAIService()

