# ML Training - Difficulty Classifier

**⚠️ OPTIONAL MODULE** - This folder contains Machine Learning training code for text difficulty classification.

## 📋 Overview

This is **NOT required** for running the main File2Learning application. The main app uses FREE AI services (Gemini/Groq) for content generation.

This ML module was designed for:
- Training custom difficulty classifier (CEFR levels: A1-C2)
- Dataset collection and preprocessing
- Research and experimentation

## 🗂️ Structure

```
ml_training/
├── datasets/
│   ├── collect_data.py       # Dataset collection scripts
│   └── raw_dataset.json      # Raw training data
├── models/
│   ├── difficulty_classifier.py  # Model architecture (DistilBERT)
│   └── __init__.py
├── training/
│   ├── train_difficulty.py   # Training scripts
│   └── __init__.py
└── utils/
    ├── data_preprocessing.py # Data preprocessing utilities
    └── __init__.py
```

## 🚀 Usage (Optional)

If you want to train your own difficulty classifier:

### Prerequisites
- NVIDIA GPU with CUDA support (RTX 3050+ recommended)
- PyTorch with CUDA
- HuggingFace Transformers

### Install Dependencies
```bash
cd ml_training
pip install -r ../backend/requirements-ai.txt
```

### Training
See `../backend/COLAB_TRAINING_GUIDE.md` for detailed instructions on training using Google Colab Pro.

## 🎯 Model Details

- **Architecture:** DistilBERT-based classifier
- **Task:** CEFR level classification (A1, A2, B1, B2, C1, C2)
- **Framework:** PyTorch + HuggingFace Transformers
- **Training:** Optimized for 4GB VRAM (RTX 3050)

## ℹ️ Notes

1. **Main app doesn't use this model** - It uses Gemini/Groq APIs instead
2. **Kept for reference** - In case you want to train custom models
3. **Can be deleted** - If you don't plan to do ML training
4. **Colab recommended** - Training on Google Colab Pro is easier than local

## 🗑️ To Remove

If you don't need ML training capabilities:
```bash
# From project root
rm -rf ml_training/
```

This won't affect the main application at all.

---

**Status:** Archived/Optional  
**Maintained:** No  
**Required:** No

