"""
Quick Start Script for AI Training
Run this file to start the full training pipeline

Usage:
    python train_ai_model.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 80)
    print("🤖 File2Learning - AI Model Training Pipeline")
    print("=" * 80)
    print()
    
    # Step 1: Collect Data
    print("📊 Step 1: Collecting training data...")
    print("-" * 80)
    result = subprocess.run([sys.executable, "-m", "app.ai.datasets.collect_data"])
    if result.returncode != 0:
        print("❌ Data collection failed!")
        return
    
    print()
    print("✅ Data collection complete!")
    print()
    
    # Step 2: Train Model
    print("🚀 Step 2: Training Difficulty Classifier...")
    print("-" * 80)
    result = subprocess.run([sys.executable, "-m", "app.ai.training.train_difficulty"])
    if result.returncode != 0:
        print("❌ Training failed!")
        return
    
    print()
    print("=" * 80)
    print("✅ AI Training Pipeline Complete!")
    print("=" * 80)
    print()
    print("📂 Output files:")
    print("  - models/difficulty_classifier/best_model.pt")
    print("  - models/difficulty_classifier/training_curves.png")
    print("  - models/difficulty_classifier/confusion_matrix.png")
    print()
    print("📋 Next steps:")
    print("  1. Review training results in models/difficulty_classifier/")
    print("  2. Test model inference")
    print("  3. Integrate into document processing pipeline")
    print()
    print("For detailed documentation, see: AI_TRAINING_GUIDE.md")
    print("=" * 80)


if __name__ == '__main__':
    main()

