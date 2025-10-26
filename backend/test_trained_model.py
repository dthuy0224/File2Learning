"""
Test the trained difficulty classifier model
Run this after downloading model from Colab
"""

import torch
from transformers import DistilBertTokenizer
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ai.models.difficulty_classifier import DifficultyClassifier

def test_model():
    """Test the trained model with sample texts"""
    
    print("=" * 70)
    print("🧪 TESTING TRAINED MODEL")
    print("=" * 70)
    
    # Check if model exists
    model_path = Path("models/difficulty_classifier/best_model.pt")
    if not model_path.exists():
        print("\n❌ Model file not found!")
        print(f"   Expected: {model_path.absolute()}")
        print("\n💡 Did you:")
        print("   1. Download model from Colab?")
        print("   2. Extract to backend/models/difficulty_classifier/?")
        return
    
    print(f"\n📥 Loading model from: {model_path}")
    
    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🎮 Device: {device}")
    
    try:
        model = DifficultyClassifier.load_model(str(model_path), device=device)
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        print("✅ Model loaded successfully!\n")
    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")
        return
    
    # Test samples
    test_samples = [
        {
            'text': "I have a cat. It is black.",
            'expected': 'A1',
            'description': 'Simple present, basic vocabulary'
        },
        {
            'text': "Last week I went to the park. The weather was nice.",
            'expected': 'A2',
            'description': 'Past tense, everyday situations'
        },
        {
            'text': "Learning a new language requires dedication and consistent practice.",
            'expected': 'B1',
            'description': 'More complex sentences, abstract concepts'
        },
        {
            'text': "The implementation of new technologies has fundamentally transformed modern business practices.",
            'expected': 'B2',
            'description': 'Advanced vocabulary, complex ideas'
        },
        {
            'text': "The paradigmatic shift in environmental policy necessitates comprehensive reevaluation of existing frameworks.",
            'expected': 'C1',
            'description': 'Academic language, sophisticated vocabulary'
        },
        {
            'text': "The epistemological implications of quantum mechanics fundamentally challenge deterministic paradigms in physics.",
            'expected': 'C2',
            'description': 'Expert-level vocabulary, highly complex concepts'
        }
    ]
    
    print("=" * 70)
    print("🔍 RUNNING INFERENCE TESTS")
    print("=" * 70)
    
    correct = 0
    adjacent_correct = 0
    level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    
    for i, sample in enumerate(test_samples, 1):
        text = sample['text']
        expected = sample['expected']
        description = sample['description']
        
        # Tokenize
        encoding = tokenizer(
            text,
            add_special_tokens=True,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        # Predict
        result = model.predict_text(input_ids, attention_mask)
        predicted = result['level']
        confidence = result['confidence']
        
        # Check accuracy
        expected_idx = level_order.index(expected)
        predicted_idx = level_order.index(predicted)
        is_correct = (expected == predicted)
        is_adjacent = abs(expected_idx - predicted_idx) <= 1
        
        if is_correct:
            correct += 1
            status = "✅ CORRECT"
        elif is_adjacent:
            status = "⚠️ CLOSE"
        else:
            status = "❌ WRONG"
        
        if is_adjacent:
            adjacent_correct += 1
        
        print(f"\n{status} Test {i}:")
        print(f"   Text: {text[:70]}...")
        print(f"   Description: {description}")
        print(f"   Expected: {expected} | Predicted: {predicted} | Confidence: {confidence:.1%}")
        
        # Show top 3 predictions
        top_3 = sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   Top 3: {' | '.join([f'{k}:{v:.1%}' for k, v in top_3])}")
    
    # Summary
    exact_accuracy = correct / len(test_samples)
    adjacent_accuracy = adjacent_correct / len(test_samples)
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    print(f"Exact Match Accuracy:    {exact_accuracy:.1%} ({correct}/{len(test_samples)})")
    print(f"Adjacent Accuracy (±1):  {adjacent_accuracy:.1%} ({adjacent_correct}/{len(test_samples)})")
    print("=" * 70)
    
    if exact_accuracy >= 0.8:
        print("✅ Excellent! Model is performing very well!")
    elif exact_accuracy >= 0.6:
        print("✅ Good! Model is working as expected!")
    elif adjacent_accuracy >= 0.8:
        print("⚠️  Model predictions are close but not exact")
    else:
        print("❌ Model needs improvement or retraining")
    
    print("\n" + "=" * 70)
    print("🎉 TEST COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Integrate model into file_processor.py")
    print("2. Test with real documents")
    print("3. Monitor accuracy with user data")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_model()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

