import asyncio
import sys
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent))

from app.services.ai_service import ollama_service


async def test_ollama_integration():
    """Test Ollama AI service integration"""

    print("🧪 Testing Ollama AI Integration...")
    print("=" * 50)

    # Test text for AI processing
    test_text = """
    Machine learning is a subset of artificial intelligence (AI) that provides systems
    the ability to automatically learn and improve from experience without being
    explicitly programmed. Machine learning focuses on the development of computer
    programs that can access data and use it to learn for themselves.

    The process of learning begins with observations or data, such as examples,
    direct experience, or instruction, in order to look for patterns in data and
    make better decisions in the future based on the examples that we provide.
    """

    print(f"📄 Test document length: {len(test_text)} characters")
    print()

    # Test 1: Summary Generation
    print("1️⃣ Testing Summary Generation...")
    try:
        summary_result = await ollama_service.generate_summary(test_text, max_length=100)
        if summary_result["success"]:
            print("✅ Summary generation successful!")
            print(f"   Summary: {summary_result['summary'][:100]}...")
            print(f"   Original length: {summary_result['original_length']} chars")
            print(f"   Summary length: {summary_result['summary_length']} chars")
        else:
            print(f"❌ Summary generation failed: {summary_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Summary test error: {str(e)}")

    print()

    # Test 2: Quiz Generation
    print("2️⃣ Testing Quiz Generation...")
    try:
        quiz_result = await ollama_service.generate_quiz(test_text, quiz_type="mixed", num_questions=3)
        if quiz_result["success"]:
            print("✅ Quiz generation successful!")
            print(f"   Generated {len(quiz_result['quiz'])} questions")
            for i, q in enumerate(quiz_result['quiz'][:2], 1):  # Show first 2 questions
                print(f"   Q{i}: {q.get('question', 'No question')[:50]}...")
        else:
            print(f"❌ Quiz generation failed: {quiz_result.get('error', 'Unknown error')}")
            if 'fallback' in quiz_result and quiz_result['fallback']:
                print(f"   Fallback quiz: {len(quiz_result['fallback'])} questions generated")
    except Exception as e:
        print(f"❌ Quiz test error: {str(e)}")

    print()

    # Test 3: Flashcard Generation
    print("3️⃣ Testing Flashcard Generation...")
    try:
        flashcard_result = await ollama_service.generate_flashcards(test_text, num_cards=3)
        if flashcard_result["success"]:
            print("✅ Flashcard generation successful!")
            print(f"   Generated {len(flashcard_result['flashcards'])} flashcards")
            for i, card in enumerate(flashcard_result['flashcards'][:2], 1):  # Show first 2 cards
                print(f"   Card{i}: {card.get('front_text', 'No front')[:30]}...")
        else:
            print(f"❌ Flashcard generation failed: {flashcard_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Flashcard test error: {str(e)}")

    print()
    print("🎯 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_ollama_integration())
