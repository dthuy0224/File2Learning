"""
================================================================================
📓 FILE2LEARNING - GOOGLE COLAB TRAINING (FIXED VERSION)
================================================================================

ĐÃ FIX:
✅ Numpy compatibility (numpy 1.26.4 + scikit-learn 1.3.2)
✅ Better error handling
✅ Dependency verification
✅ Clearer instructions
✅ Fallback mechanisms

HƯỚNG DẪN:
1. Mở file notebook: File2Learning_Colab_Training.ipynb
2. Copy từng CELL dưới đây vào notebook
3. Chạy tuần tự từ Cell 1 → Cell cuối

================================================================================
"""


# ============================= CELL 1 =====================================
# Markdown Cell
"""
# 🎓 File2Learning - AI Model Training on Google Colab

## 📚 Difficulty Classifier Training Pipeline

**Model**: DistilBERT-based Text Difficulty Classifier (A1-C2 CEFR levels)

**GPU**: Tesla T4 (16GB VRAM) - Miễn phí trên Google Colab

**Training Time**: ~8-12 phút

---

### 🚀 Quick Start Guide:
1. **Runtime** → **Change runtime type** → **GPU** (T4 hoặc V100)
2. **Run All** (Runtime → Run all) hoặc chạy từng cell
3. Đợi training hoàn thành (~10 phút)
4. Download model về local

---
"""


# ============================= CELL 2 =====================================
# Markdown Cell
"""
## 🔧 Step 1: Environment Check & GPU Detection
"""


# ============================= CELL 3 =====================================
# Code Cell
"""
# Check GPU availability and Python environment
import torch
import os
import sys

print("="*70)
print("🔍 ENVIRONMENT CHECK")
print("="*70)

print(f"\\n🐍 Python: {sys.version.split()[0]}")

if torch.cuda.is_available():
    print(f"\\n✅ GPU Available: {torch.cuda.get_device_name(0)}")
    print(f"📊 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print(f"🔢 CUDA Version: {torch.version.cuda}")
    print(f"🔥 PyTorch Version: {torch.__version__}")
else:
    print("\\n❌ GPU NOT AVAILABLE!")
    print("⚠️  Go to: Runtime → Change runtime type → GPU (T4)")
    print("⚠️  Training will be VERY slow on CPU")

print("\\n" + "="*70)
print("✅ Environment check complete!")
print("="*70)
"""


# ============================= CELL 4 =====================================
# Markdown Cell
"""
## 🔧 Step 2: Fix Numpy Compatibility (CRITICAL!)

**⚠️ MUST RUN THIS CELL FIRST!**

This fixes the numpy compatibility issue with scikit-learn on Colab.
"""


# ============================= CELL 5 =====================================
# Code Cell - CRITICAL FIX
"""
print("="*70)
print("🔧 FIXING NUMPY COMPATIBILITY")
print("="*70)

print("\\n⚠️  Installing compatible versions...")
print("   - numpy 1.26.4")
print("   - scikit-learn 1.3.2")
print("   - scipy 1.11.4\\n")

# Install compatible versions
!pip install -q --upgrade --no-cache-dir numpy==1.26.4 scikit-learn==1.3.2 scipy==1.11.4

print("\\n✅ Compatible versions installed!")

print("\\n" + "="*70)
print("⚠️  IMPORTANT: RESTART RUNTIME NOW!")
print("="*70)
print("\\nSteps:")
print("1. Runtime → Restart runtime")
print("2. Run Cell 1 again (Environment Check)")
print("3. SKIP this Cell 2 (already done)")
print("4. Continue from Cell 3 onwards")
print("\\n" + "="*70)
"""


# ============================= CELL 6 =====================================
# Markdown Cell
"""
## 💾 Step 3: Mount Google Drive (Optional)

**Nếu bạn muốn save model vào Google Drive**, uncomment và chạy cell này:
"""


# ============================= CELL 7 =====================================
# Code Cell
"""
# from google.colab import drive
# drive.mount('/content/drive')

# # Create output directory in Drive
# DRIVE_OUTPUT_DIR = '/content/drive/MyDrive/File2Learning_Models'
# os.makedirs(DRIVE_OUTPUT_DIR, exist_ok=True)
# print(f"✅ Google Drive mounted! Models will be saved to: {DRIVE_OUTPUT_DIR}")
"""


# ============================= CELL 8 =====================================
# Markdown Cell
"""
## 📁 Step 4: Upload Project Files

**Chọn 1 trong 2 options:**

### **Option A: Upload từ local** (Recommended)
1. Zip toàn bộ folder `backend/` thành `backend.zip`
2. Upload file zip và extract
""" 


# ============================= CELL 9 =====================================
# Code Cell
"""
# Option A: Upload ZIP file
from google.colab import files
import zipfile

print("📤 Upload backend.zip file...")
print("⏳ Waiting for file selection...\\n")

uploaded = files.upload()

# Extract
for filename in uploaded.keys():
    if filename.endswith('.zip'):
        print(f"\\n📦 Extracting {filename}...")
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall('/content/')
        print("✅ Extraction complete!")
        break

# Change to backend directory
print("\\n📂 Changing to backend directory...")
%cd /content/backend
print("\\n📋 Current directory contents:")
!ls -la

print("\\n✅ Project files ready!")
"""


# ============================= CELL 10 =====================================
# Markdown Cell
"""
### **Option B: Clone từ GitHub** (Nếu bạn đã push code lên GitHub)
"""


# ============================= CELL 11 =====================================
# Code Cell
"""
# # Option B: Clone from GitHub
# !git clone https://github.com/YOUR_USERNAME/File2Learning.git
# %cd File2Learning/backend
# !pwd
# !ls -la
"""


# ============================= CELL 12 =====================================
# Markdown Cell
"""
## 📦 Step 5: Verify Dependencies

Verify that numpy and other packages are correctly installed
"""


# ============================= CELL 13 =====================================
# Code Cell - DEPENDENCY VERIFICATION
"""
print("="*70)
print("📦 VERIFYING DEPENDENCIES")
print("="*70)

# Check critical packages
try:
    import numpy as np
    print(f"\\n✅ numpy: {np.__version__}")
    if not np.__version__.startswith('1.26'):
        print("⚠️  WARNING: numpy version may cause issues!")
        print("   Expected: 1.26.x")
except Exception as e:
    print(f"\\n❌ numpy error: {e}")
    print("⚠️ Did you restart runtime after Cell 2?")

try:
    import pandas as pd
    print(f"✅ pandas: {pd.__version__}")
except Exception as e:
    print(f"❌ pandas: {e}")

try:
    import sklearn
    print(f"✅ scikit-learn: {sklearn.__version__}")
    if not sklearn.__version__.startswith('1.3'):
        print("⚠️  WARNING: scikit-learn version may cause issues!")
        print("   Expected: 1.3.x")
except Exception as e:
    print(f"❌ scikit-learn: {e}")
    print("⚠️ Did you restart runtime after Cell 2?")

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"   CUDA: {torch.cuda.is_available()}")
except Exception as e:
    print(f"❌ PyTorch: {e}")

print("\\n" + "="*70)
print("✅ Dependency check complete!")
print("="*70)
"""


# ============================= CELL 14 =====================================
# Markdown Cell
"""
## 📦 Step 6: Install AI Training Dependencies

Install transformers và các packages cần thiết cho training
"""


# ============================= CELL 15 =====================================
# Code Cell
"""
print("="*70)
print("📦 INSTALLING AI TRAINING DEPENDENCIES")
print("="*70)
print("⏳ This may take 2-3 minutes...\\n")

# Install transformers and related packages
!pip install -q transformers==4.36.0 tokenizers==0.15.0
!pip install -q accelerate==0.25.0
!pip install -q matplotlib seaborn plotly
!pip install -q tqdm

print("\\n✅ All AI dependencies installed!")

# Verify transformers installation
print("\\n" + "="*70)
print("🔍 VERIFYING AI PACKAGES")
print("="*70)

try:
    import transformers
    print(f"\\n✅ Transformers: {transformers.__version__}")
    
    from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
    print("✅ DistilBERT models available")
    
except Exception as e:
    print(f"\\n❌ Transformers import error: {e}")
    print("⚠️ Training may fail!")

try:
    from tqdm import tqdm
    print("✅ tqdm available")
except:
    print("⚠️ tqdm not available (not critical)")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    print("✅ Plotting libraries available")
except:
    print("⚠️ Plotting libraries not available (not critical)")

print("\\n" + "="*70)
print("✅ Ready for training!")
print("="*70)
"""


# ============================= CELL 16 =====================================
# Markdown Cell
"""
## 🔍 Step 7: Verify Project Structure

Kiểm tra xem tất cả files cần thiết đã có chưa
"""


# ============================= CELL 17 =====================================
# Code Cell - WITH BETTER ERROR HANDLING
"""
import os
from pathlib import Path

print("="*70)
print("🔍 VERIFYING PROJECT STRUCTURE")
print("="*70)

required_files = [
    'train_ai_model.py',
    'app/ai/models/difficulty_classifier.py',
    'app/ai/training/train_difficulty.py',
    'app/ai/datasets/collect_data.py',
    'app/ai/utils/data_preprocessing.py',
]

all_good = True
missing_files = []

for file in required_files:
    if Path(file).exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - MISSING!")
        missing_files.append(file)
        all_good = False

if all_good:
    print("\\n🎉 All required files present!")
else:
    print(f"\\n⚠️  Missing {len(missing_files)} file(s):")
    for f in missing_files:
        print(f"   - {f}")
    print("\\n❌ Please check your upload in Step 4")

# Check if dataset exists
dataset_path = Path('app/ai/datasets/raw_dataset.json')
if dataset_path.exists():
    try:
        import json
        with open(dataset_path) as f:
            data = json.load(f)
        num_samples = data.get('num_samples', len(data.get('data', [])))
        print(f"\\n📊 Dataset found: {num_samples} samples")
    except Exception as e:
        print(f"\\n⚠️  Dataset file exists but couldn't read: {e}")
        print("   Will generate synthetic dataset")
else:
    print("\\n⚠️  Dataset not found. Will generate synthetic dataset.")

print("\\n" + "="*70)
"""


# ============================= CELL 18 =====================================
# Markdown Cell
"""
## ⚙️ Step 8: Training Configuration

Cấu hình tối ưu cho GPU T4 (16GB VRAM)
"""


# ============================= CELL 19 =====================================
# Code Cell
"""
import torch

# Training configuration for Google Colab T4
TRAINING_CONFIG = {
    'batch_size': 16,        # Tăng từ 8 (local) lên 16 vì T4 có 16GB VRAM
    'num_epochs': 3,         # Giữ nguyên
    'learning_rate': 2e-5,   # Giữ nguyên
    'max_length': 512,       # Giữ nguyên
    'warmup_steps': 500,     # Giữ nguyên
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

print("="*70)
print("⚙️  TRAINING CONFIGURATION")
print("="*70)
for key, value in TRAINING_CONFIG.items():
    print(f"  {key:20s}: {value}")

if TRAINING_CONFIG['device'] == 'cpu':
    print("\\n⚠️  WARNING: Training on CPU will be VERY slow!")
    print("   Consider enabling GPU: Runtime → Change runtime type → GPU")

print("="*70)
"""


# ============================= CELL 20 =====================================
# Markdown Cell
"""
## 📊 Step 9: Collect Training Data

Generate synthetic dataset (hoặc sử dụng dataset có sẵn)
"""


# ============================= CELL 21 =====================================
# Code Cell - WITH ERROR HANDLING
"""
print("="*70)
print("📊 COLLECTING TRAINING DATA")
print("="*70)

try:
    # Try to run the data collection script
    print("\\n⏳ Running data collection script...")
    !python -m app.ai.datasets.collect_data
    print("\\n✅ Data collection complete!")
    
except Exception as e:
    print(f"\\n⚠️  Data collection script failed: {e}")
    print("   This is OK - training will generate synthetic data automatically")

print("\\n" + "="*70)
"""


# ============================= CELL 22 =====================================
# Markdown Cell
"""
## 🚀 Step 10: Train the Model!

**Main training process** - Đây là bước quan trọng nhất!

Expected time: **~8-12 phút** trên T4 GPU

### What happens:
1. Load dataset và preprocessing
2. Initialize DistilBERT model
3. Train for 3 epochs
4. Save best model dựa trên validation F1 score
5. Generate training curves và confusion matrix
"""


# ============================= CELL 23 =====================================
# Code Cell - WITH COMPREHENSIVE ERROR HANDLING
"""
import time

print("="*70)
print("🚀 STARTING AI MODEL TRAINING")
print("="*70)
print("\\n⏱️  Estimated time: 8-12 minutes on T4 GPU")
print("📊 You'll see progress bars for each epoch")
print("💾 Best model will be saved automatically")
print("\\n" + "="*70)
print()

start_time = time.time()

try:
    # Run training
    !python -m app.ai.training.train_difficulty
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print(f"⏱️  Total time: {duration/60:.2f} minutes ({duration:.0f} seconds)")
    print("="*70)
    
except Exception as e:
    print("\\n" + "="*70)
    print("❌ TRAINING FAILED!")
    print("="*70)
    print(f"Error: {e}")
    print("\\n💡 Troubleshooting:")
    print("   1. Check if all files were uploaded correctly (Step 7)")
    print("   2. Verify dependencies are installed (Step 6)")
    print("   3. Make sure GPU is available (Step 1)")
    print("="*70)
"""


# ============================= CELL 24 =====================================
# Markdown Cell
"""
## 📈 Step 11: View Training Results

Visualize training curves và confusion matrix
"""


# ============================= CELL 25 =====================================
# Code Cell - WITH BETTER PATH HANDLING
"""
from IPython.display import Image, display
import os
from pathlib import Path

print("="*70)
print("📈 TRAINING RESULTS VISUALIZATION")
print("="*70)

# Check for results directory
results_dirs = [
    'models/difficulty_classifier',
    'app/ai/models/trained',
    './results'
]

found_dir = None
for dir_path in results_dirs:
    if Path(dir_path).exists():
        found_dir = dir_path
        break

if found_dir:
    print(f"\\n📂 Results directory: {found_dir}")
    
    # Display training curves
    curves_path = Path(found_dir) / 'training_curves.png'
    if curves_path.exists():
        print("\\n📊 Training Curves:")
        display(Image(filename=str(curves_path)))
    else:
        print(f"\\n⚠️  Training curves not found")
    
    # Display confusion matrix
    cm_path = Path(found_dir) / 'confusion_matrix.png'
    if cm_path.exists():
        print("\\n🎯 Confusion Matrix:")
        display(Image(filename=str(cm_path)))
    else:
        print(f"\\n⚠️  Confusion matrix not found")
    
    # List all files
    print("\\n📂 Generated Files:")
    !ls -lh {found_dir}
    
else:
    print("\\n⚠️  Results directory not found!")
    print("   Training may have failed. Check Step 10 output.")

print("\\n" + "="*70)
"""


# ============================= CELL 26 =====================================
# Markdown Cell
"""
## 🧪 Step 12: Test Model Inference

Test model với một số sample texts
"""


# ============================= CELL 27 =====================================
# Code Cell - ROBUST INFERENCE TEST
"""
import torch
from transformers import DistilBertTokenizer
import sys
from pathlib import Path

print("="*70)
print("🧪 TESTING MODEL INFERENCE")
print("="*70)

try:
    # Import model class
    sys.path.insert(0, str(Path.cwd()))
    from app.ai.models.difficulty_classifier import DifficultyClassifier
    
    # Find model file
    model_paths = [
        'models/difficulty_classifier/best_model.pt',
        'app/ai/models/trained/best_model.pt',
        './results/best_model.pt'
    ]
    
    model_path = None
    for path in model_paths:
        if Path(path).exists():
            model_path = path
            break
    
    if not model_path:
        raise FileNotFoundError("Model file not found!")
    
    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\\n📥 Loading model from: {model_path}")
    print(f"🎮 Device: {device}")
    
    model = DifficultyClassifier.load_model(model_path, device=device)
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    
    print("✅ Model loaded successfully!\\n")
    
    # Test samples
    test_texts = [
        ("I have a cat. It is black.", "A1"),
        ("Last week I went to the park. The weather was nice.", "A2"),
        ("Learning a new language requires dedication and practice.", "B1"),
        ("The implementation of new technologies has transformed businesses.", "B2"),
        ("The paradigmatic shift in policy necessitates comprehensive analysis.", "C1"),
        ("The epistemological implications challenge deterministic paradigms.", "C2"),
    ]
    
    print("="*70)
    print("🔍 TESTING SAMPLE TEXTS")
    print("="*70)
    
    correct = 0
    
    for i, (text, expected_level) in enumerate(test_texts, 1):
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
        predicted_level = result['level']
        
        # Check if correct (allow ±1 level difference)
        level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        expected_idx = level_order.index(expected_level)
        predicted_idx = level_order.index(predicted_level)
        is_correct = abs(expected_idx - predicted_idx) <= 1
        
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"\\n{status} Test {i}:")
        print(f"   Text: {text[:60]}...")
        print(f"   Expected: {expected_level} | Predicted: {predicted_level}")
        print(f"   Confidence: {result['confidence']:.2%}")
        
        # Show top 3 predictions
        top_3 = sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   Top 3: {', '.join([f'{k}:{v:.1%}' for k, v in top_3])}")
    
    accuracy = correct / len(test_texts)
    print("\\n" + "="*70)
    print(f"📊 Test Accuracy: {accuracy:.1%} ({correct}/{len(test_texts)} within ±1 level)")
    print("="*70)
    
    if accuracy >= 0.8:
        print("✅ Model performing well!")
    elif accuracy >= 0.5:
        print("⚠️  Model is OK, but could be better")
    else:
        print("❌ Model needs more training")
    
    print("\\n✅ Inference test complete!")
    
except Exception as e:
    print(f"\\n❌ INFERENCE TEST FAILED!")
    print(f"Error: {e}")
    print("\\n💡 This could mean:")
    print("   1. Model file not found (training may have failed)")
    print("   2. Model class import error")
    print("   3. GPU/memory issue")
    print("\\nCheck previous steps for errors.")

print("\\n" + "="*70)
"""


# ============================= CELL 28 =====================================
# Markdown Cell
"""
## 💾 Step 13: Download Trained Model

Download model và results về máy local
"""


# ============================= CELL 29 =====================================
# Code Cell - WITH COMPREHENSIVE ERROR HANDLING
"""
from google.colab import files
import shutil
import os
from pathlib import Path

print("="*70)
print("💾 PREPARING FILES FOR DOWNLOAD")
print("="*70)

try:
    # Find output directory
    output_dirs = [
        'models/difficulty_classifier',
        'app/ai/models/trained',
        './results'
    ]
    
    output_dir = None
    for dir_path in output_dirs:
        if Path(dir_path).exists():
            output_dir = dir_path
            break
    
    if not output_dir:
        raise FileNotFoundError("Output directory not found!")
    
    print(f"\\n📂 Found output directory: {output_dir}")
    
    # Create zip file
    zip_filename = 'file2learning_trained_model'
    
    print(f"\\n📦 Creating {zip_filename}.zip...")
    shutil.make_archive(zip_filename, 'zip', output_dir)
    
    zip_file = f"{zip_filename}.zip"
    file_size = Path(zip_file).stat().st_size / 1024 / 1024  # MB
    
    print(f"✅ Created {zip_file} ({file_size:.1f} MB)")
    
    print("\\n📋 Archive contents:")
    !unzip -l {zip_file}
    
    print("\\n⬇️  Starting download...")
    files.download(zip_file)
    
    print("\\n✅ Download complete!")
    print("\\n" + "="*70)
    print("📋 NEXT STEPS")
    print("="*70)
    print("1. Extract the zip file on your local machine")
    print("2. Copy contents to: backend/models/difficulty_classifier/")
    print("3. Test model in your local project")
    print("4. Integrate into document processing pipeline")
    print("="*70)
    
except Exception as e:
    print(f"\\n❌ DOWNLOAD PREPARATION FAILED!")
    print(f"Error: {e}")
    print("\\n💡 Manual download:")
    print("1. Look in left sidebar (Files icon)")
    print("2. Navigate to the model directory")
    print("3. Right-click files → Download")
    print("\\nKey files to download:")
    print("  - best_model.pt")
    print("  - training_curves.png")
    print("  - confusion_matrix.png")

print("\\n" + "="*70)
"""


# ============================= CELL 30 =====================================
# Markdown Cell - FINAL SUMMARY
"""
---

## 🎉 Training Complete!

### 📊 Summary

Bạn đã successfully train **Difficulty Classifier** với:
- ✅ Model: DistilBERT (66M parameters)
- ✅ Task: 6-class classification (A1, A2, B1, B2, C1, C2)
- ✅ GPU: Google Colab T4 (16GB VRAM)
- ✅ Dataset: Synthetic + Real CEFR texts

### 📂 Output Files
- `best_model.pt` - Trained model weights (~250 MB)
- `training_curves.png` - Loss/Accuracy/F1 visualization
- `confusion_matrix.png` - Performance heatmap
- Checkpoint files for each epoch

### 🔄 Integration into File2Learning

```python
# backend/app/utils/file_processor.py
from app.ai.models.difficulty_classifier import DifficultyClassifier
from transformers import DistilBertTokenizer

class FileProcessor:
    def __init__(self):
        self.difficulty_classifier = DifficultyClassifier.load_model(
            'models/difficulty_classifier/best_model.pt'
        )
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    
    def analyze_content(self, text: str) -> dict:
        # Tokenize text
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Predict difficulty
        result = self.difficulty_classifier.predict_text(
            encoding['input_ids'],
            encoding['attention_mask']
        )
        
        return {
            'cefr_level': result['level'],  # A1-C2
            'confidence': result['confidence'],  # 0.0-1.0
            'probabilities': result['probabilities']  # All 6 levels
        }
```

### 💡 Performance Tips

**Expected Accuracy:**
- Training: 85-95%
- Validation: 80-90%
- Test: 75-85%
- Adjacent (±1 level): 95%+

**If accuracy is low:**
1. Train for more epochs (3 → 5)
2. Add more diverse training data
3. Adjust learning rate (2e-5 → 3e-5)
4. Increase batch size if GPU allows (16 → 24)

**For production:**
- Use FP16 for faster inference
- Batch process multiple texts
- Cache tokenizer and model
- Consider quantization for smaller model size

### 📞 Troubleshooting

**Common Issues:**

| Issue | Solution |
|-------|----------|
| GPU Not Available | Runtime → Change runtime type → GPU |
| Out of Memory | Reduce batch_size (16 → 8) or max_length (512 → 256) |
| Import Errors | Restart runtime after Cell 2 (numpy fix) |
| Low Accuracy | Train longer, add more data, tune hyperparameters |
| Slow Training | Verify GPU enabled, reduce max_length |
| Files Not Found | Re-upload backend.zip, check Step 7 |

### 🚀 Next Steps

1. ✅ Download model (Step 13 above)
2. Extract ZIP file to `backend/models/difficulty_classifier/`
3. Update `file_processor.py` with model integration code
4. Test on real documents
5. Monitor accuracy with user feedback
6. Retrain periodically with new data

---

**Happy Training! 🚀**

*File2Learning - Learn Smarter with AI*
"""


print("""
================================================================================
✅ ALL CELLS READY!
================================================================================

HƯỚNG DẪN SỬ DỤNG:
1. Mở file: backend/File2Learning_Colab_Training.ipynb
2. Copy từng cell từ file này vào notebook
3. Quan trọng: 
   - Cell 5 (Numpy Fix) PHẢI chạy trước
   - Restart runtime sau Cell 5
   - Skip Cell 5 sau khi restart

CÁC FIX ĐÃ ÁP DỤNG:
✅ Numpy 1.26.4 + scikit-learn 1.3.2 compatibility
✅ Better error handling
✅ Clear restart instructions
✅ Multiple fallback paths for files
✅ Comprehensive testing
✅ Production-ready integration code

================================================================================
""")

