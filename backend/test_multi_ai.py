"""
Quick test script for Multi-AI Service
Run this to verify your AI providers are working
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_ai_service():
    from app.services.multi_ai_service import multi_ai_service
    
    print("=" * 60)
    print("🧪 Testing Multi-AI Service")
    print("=" * 60)
    
    # Check API keys
    print("\n📋 Checking API Keys:")
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    print(f"   Gemini API Key: {'✅ Set' if gemini_key else '❌ Missing'}")
    if gemini_key:
        print(f"      Preview: {gemini_key[:20]}...")
    
    print(f"   Groq API Key:   {'✅ Set' if groq_key else '❌ Missing'}")
    if groq_key:
        print(f"      Preview: {groq_key[:20]}...")
    
    # Test text
    test_text = """
    Artificial Intelligence (AI) is transforming education. Machine learning algorithms 
    can personalize learning experiences, adapt to student needs, and provide instant 
    feedback. Natural Language Processing enables intelligent tutoring systems.
    """
    
    print("\n" + "=" * 60)
    print("🧪 Test 1: Generate Summary")
    print("=" * 60)
    
    result = await multi_ai_service.generate_summary(test_text, max_length=50)
    
    if result["success"]:
        print(f"✅ SUCCESS!")
        print(f"   Provider: {result.get('ai_provider', 'unknown')}")
        print(f"   Model: {result.get('ai_model', 'unknown')}")
        print(f"   Summary: {result.get('summary', '')[:100]}...")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("🧪 Test 2: Generate Quiz")
    print("=" * 60)
    
    result = await multi_ai_service.generate_quiz(test_text, quiz_type="mcq", num_questions=2)
    
    if result["success"]:
        print(f"✅ SUCCESS!")
        print(f"   Provider: {result.get('ai_provider', 'unknown')}")
        print(f"   Model: {result.get('ai_model', 'unknown')}")
        print(f"   Questions generated: {len(result.get('quiz', []))}")
        if result.get('quiz'):
            print(f"   First question: {result['quiz'][0].get('question', '')[:80]}...")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("🧪 Test 3: Generate Flashcards")
    print("=" * 60)
    
    result = await multi_ai_service.generate_flashcards(test_text, num_cards=3)
    
    if result["success"]:
        print(f"✅ SUCCESS!")
        print(f"   Provider: {result.get('ai_provider', 'unknown')}")
        print(f"   Model: {result.get('ai_model', 'unknown')}")
        print(f"   Flashcards generated: {len(result.get('flashcards', []))}")
        if result.get('flashcards'):
            first_card = result['flashcards'][0]
            print(f"   First card front: {first_card.get('front_text', '')[:50]}...")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("📊 Provider Statistics")
    print("=" * 60)
    
    stats = multi_ai_service.get_stats()
    print(f"\n Available Providers:")
    for provider, available in stats["available_providers"].items():
        status = "✅ Available" if available else "❌ Not Available"
        print(f"   {provider.capitalize()}: {status}")
    
    print(f"\n Usage Stats:")
    for provider, data in stats["providers"].items():
        success = data["success"]
        failures = data["failures"]
        total = success + failures
        if total > 0:
            success_rate = (success / total) * 100
            print(f"   {provider.capitalize()}: {success} success, {failures} failures ({success_rate:.1f}% success rate)")
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not gemini_key and not groq_key:
        print("   ⚠️  No API keys configured!")
        print("   📝 Get FREE Gemini key: https://makersuite.google.com/app/apikey")
        print("   📝 Get FREE Groq key: https://console.groq.com/keys")
    elif not gemini_key:
        print("   💡 Add Gemini API key for better performance")
        print("   📝 Get it here: https://makersuite.google.com/app/apikey")
    elif not groq_key:
        print("   💡 Add Groq API key for faster backup")
        print("   📝 Get it here: https://console.groq.com/keys")
    else:
        print("   ✅ All API keys configured! You're all set!")
    
    print("\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_ai_service())
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

