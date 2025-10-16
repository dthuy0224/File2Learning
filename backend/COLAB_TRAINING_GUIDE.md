# 🚀 Google Colab Training Guide

Hướng dẫn chi tiết train Difficulty Classifier trên Google Colab Pro

---

## 📋 Preparation (Trên máy local)

### Step 1: Zip Dataset

```powershell
# Trong backend directory
cd "D:\The Last Dances\ATI\Final\File2Learning\backend"

# Tạo zip file
Compress-Archive -Path "app\ai\datasets\raw_dataset.json" -DestinationPath "dataset_for_colab.zip"
```

Hoặc thủ công:
1. Mở folder `backend/app/ai/datasets/`
2. Right-click `raw_dataset.json` → Send to → Compressed folder

---

## 🌐 Setup Google Colab

### Step 1: Tạo New Notebook

1. Vào https://colab.research.google.com/
2. File → New notebook
3. Runtime → Change runtime type → **GPU** (T4 hoặc V100)

### Step 2: Check GPU

Copy & paste cell đầu tiên:

```python
# Cell 1: Check GPU
!nvidia-smi

import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
```

**Expected output:**
```
GPU: Tesla T4
VRAM: 15.75 GB
CUDA: True
```

---

## 📦 Install & Upload

### Cell 2: Install Dependencies

```python
# Cell 2: Install packages
!pip install -q transformers==4.36.0 datasets==2.16.0 accelerate==0.25.0
!pip install -q scikit-learn matplotlib seaborn tqdm

print("✅ Installed!")
```

### Cell 3: Upload Dataset

```python
# Cell 3: Upload dataset
from google.colab import files
import json

# Upload file
print("Click 'Choose Files' và chọn raw_dataset.json")
uploaded = files.upload()

# Verify
with open('raw_dataset.json', 'r') as f:
    data = json.load(f)
    print(f"\n✅ Loaded {len(data['data'])} samples")
    
# Show distribution
import pandas as pd
df = pd.DataFrame(data['data'])
print(f"\nLabel distribution:\n{df['label'].value_counts().sort_index()}")
```

---

## 🤖 Training Code

### Cell 4: Model Architecture

```python
# Cell 4: Define model
import torch
import torch.nn as nn
from transformers import DistilBertModel

class DifficultyClassifier(nn.Module):
    LABEL_MAP = {0: 'A1', 1: 'A2', 2: 'B1', 3: 'B2', 4: 'C1', 5: 'C2'}
    
    def __init__(self, num_labels=6, dropout=0.3):
        super().__init__()
        self.num_labels = num_labels
        self.distilbert = DistilBertModel.from_pretrained('distilbert-base-uncased')
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.distilbert.config.hidden_size, num_labels)
        self.classifier.weight.data.normal_(mean=0.0, std=0.02)
        self.classifier.bias.data.zero_()
    
    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.distilbert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0]
        pooled = self.dropout(pooled)
        logits = self.classifier(pooled)
        
        loss = None
        if labels is not None:
            loss = nn.CrossEntropyLoss()(logits, labels)
        
        return {
            'loss': loss,
            'logits': logits,
            'predictions': torch.argmax(logits, dim=-1),
            'probabilities': torch.softmax(logits, dim=-1)
        }

print("✅ Model defined!")
```

### Cell 5: Prepare Data

```python
# Cell 5: Prepare dataset
from sklearn.model_selection import train_test_split
from transformers import DistilBertTokenizer
from torch.utils.data import Dataset, DataLoader

# Label mapping
LABEL_MAP = {'A1': 0, 'A2': 1, 'B1': 2, 'B2': 3, 'C1': 4, 'C2': 5}
df['label_id'] = df['label'].map(LABEL_MAP)

# Split
train_df, temp = train_test_split(df, test_size=0.3, stratify=df['label'], random_state=42)
val_df, test_df = train_test_split(temp, test_size=0.5, stratify=temp['label'], random_state=42)

print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

# Tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Dataset class
class DifficultyDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': enc['input_ids'].flatten(),
            'attention_mask': enc['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

# Create datasets & loaders
train_dataset = DifficultyDataset(train_df['text'].tolist(), train_df['label_id'].tolist(), tokenizer)
val_dataset = DifficultyDataset(val_df['text'].tolist(), val_df['label_id'].tolist(), tokenizer)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

print(f"✅ Data ready! Train batches: {len(train_loader)}")
```

### Cell 6: Training Setup

```python
# Cell 6: Setup training
from transformers import AdamW, get_linear_schedule_with_warmup
from sklearn.metrics import accuracy_score, f1_score

device = torch.device('cuda')
model = DifficultyClassifier().to(device)

print(f"Device: {device}")
print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

# Optimizer & Scheduler
optimizer = AdamW(model.parameters(), lr=2e-5)
num_epochs = 3
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=500,
    num_training_steps=len(train_loader) * num_epochs
)

print("✅ Ready to train!")
```

### Cell 7: Training Functions

```python
# Cell 7: Train & eval functions
from tqdm.notebook import tqdm

def train_epoch(model, loader, optimizer, scheduler, device):
    model.train()
    total_loss = 0
    for batch in tqdm(loader, desc='Training'):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        outputs = model(input_ids, attention_mask, labels)
        outputs['loss'].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        
        total_loss += outputs['loss'].item()
    
    return total_loss / len(loader)

def evaluate(model, loader, device):
    model.eval()
    total_loss = 0
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for batch in tqdm(loader, desc='Evaluating'):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids, attention_mask, labels)
            total_loss += outputs['loss'].item()
            all_preds.extend(outputs['predictions'].cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    return {
        'loss': total_loss / len(loader),
        'accuracy': accuracy_score(all_labels, all_preds),
        'f1': f1_score(all_labels, all_preds, average='weighted')
    }

print("✅ Functions ready!")
```

### Cell 8: Main Training Loop

```python
# Cell 8: Train!
best_f1 = 0.0
history = {'train_loss': [], 'val_loss': [], 'val_acc': [], 'val_f1': []}

print("🚀 Starting training...\n" + "="*60)

for epoch in range(num_epochs):
    print(f"\nEpoch {epoch+1}/{num_epochs}")
    print("-"*60)
    
    # Train
    train_loss = train_epoch(model, train_loader, optimizer, scheduler, device)
    print(f"Train Loss: {train_loss:.4f}")
    
    # Evaluate
    val_metrics = evaluate(model, val_loader, device)
    print(f"Val Loss: {val_metrics['loss']:.4f}")
    print(f"Val Accuracy: {val_metrics['accuracy']:.4f}")
    print(f"Val F1: {val_metrics['f1']:.4f}")
    
    # Save history
    history['train_loss'].append(train_loss)
    history['val_loss'].append(val_metrics['loss'])
    history['val_acc'].append(val_metrics['accuracy'])
    history['val_f1'].append(val_metrics['f1'])
    
    # Save best
    if val_metrics['f1'] > best_f1:
        best_f1 = val_metrics['f1']
        torch.save({
            'model_state_dict': model.state_dict(),
            'num_labels': 6,
            'label_map': DifficultyClassifier.LABEL_MAP
        }, 'best_model.pt')
        print(f"✅ Best model saved! F1: {best_f1:.4f}")

print("\n" + "="*60)
print(f"🎉 Training complete! Best F1: {best_f1:.4f}")
```

### Cell 9: Visualize Results

```python
# Cell 9: Plot results
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Loss
axes[0].plot(history['train_loss'], 'o-', label='Train')
axes[0].plot(history['val_loss'], 'o-', label='Val')
axes[0].set_title('Loss')
axes[0].legend()
axes[0].grid(True)

# Accuracy
axes[1].plot(history['val_acc'], 'o-', color='green')
axes[1].set_title('Validation Accuracy')
axes[1].grid(True)

# F1
axes[2].plot(history['val_f1'], 'o-', color='orange')
axes[2].set_title('Validation F1 Score')
axes[2].grid(True)

plt.tight_layout()
plt.savefig('training_curves.png', dpi=300)
plt.show()

print("✅ Saved training_curves.png")
```

### Cell 10: Test Prediction

```python
# Cell 10: Test examples
test_texts = [
    "I have a cat.",
    "Yesterday I went to the park with my friends.",
    "Climate change requires international cooperation.",
    "The paradigmatic shift necessitates reevaluation."
]

model.eval()
for text in test_texts:
    enc = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        out = model(enc['input_ids'].to(device), enc['attention_mask'].to(device))
    
    pred_idx = out['predictions'].item()
    conf = out['probabilities'][0][pred_idx].item()
    label = DifficultyClassifier.LABEL_MAP[pred_idx]
    
    print(f"{text[:50]:50s} → {label} ({conf:.1%})")
```

### Cell 11: Download Model

```python
# Cell 11: Download
from google.colab import files

# Download model
files.download('best_model.pt')
files.download('training_curves.png')

print("✅ Files downloaded!")
print("\n📥 Next: Copy best_model.pt to:")
print("D:\\The Last Dances\\ATI\\Final\\File2Learning\\backend\\models\\difficulty_classifier\\")
```

---

## 📊 Expected Results

```
Epoch 1: Train Loss: 1.2 → Val Acc: 65% → Val F1: 0.62
Epoch 2: Train Loss: 0.3 → Val Acc: 82% → Val F1: 0.80
Epoch 3: Train Loss: 0.15 → Val Acc: 87% → Val F1: 0.85

✅ Best F1 Score: 0.85
✅ Training time: 1-2 hours on T4
```

---

## 🎯 After Training

### 1. Download Model

- File `best_model.pt` (~300MB) sẽ tự động download
- Hoặc copy từ Colab files panel

### 2. Copy vào Local Project

```
D:\The Last Dances\ATI\Final\File2Learning\backend\models\difficulty_classifier\best_model.pt
```

### 3. Test Local

```powershell
# Test model loaded
cd backend
python -c "import torch; model = torch.load('models/difficulty_classifier/best_model.pt'); print('Model loaded!', model.keys())"
```

---

## 🐛 Troubleshooting

### GPU Not Available

```python
# Runtime → Change runtime type → GPU
# Then restart runtime
```

### Out of Memory

```python
# Reduce batch size in Cell 5
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)  # 16 → 8
```

### Upload Failed

```python
# Try alternative upload
from google.colab import drive
drive.mount('/content/drive')

# Copy from Drive
!cp /content/drive/MyDrive/raw_dataset.json .
```

---

## ✅ Checklist

- [ ] GPU enabled (T4 or V100)
- [ ] Dataset uploaded (1,203 samples)
- [ ] All cells run successfully
- [ ] Training completed (3 epochs)
- [ ] Model downloaded (best_model.pt)
- [ ] Model copied to local project
- [ ] Tested predictions

---

## 🎓 Notes for Academic Project

**Time:** ~1.5-2 hours total (including upload/download)

**Show in presentation:**
- Training curves screenshot
- Confusion matrix
- Model performance metrics
- Before/After comparison

**Files to keep:**
- `best_model.pt` - Trained model
- `training_curves.png` - Visualization
- Colab notebook - Training log

---

**Questions?** Check `AI_TRAINING_GUIDE.md` hoặc ask team!

Good luck! 🚀

