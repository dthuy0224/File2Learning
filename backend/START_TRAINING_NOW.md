# 🚀 BẮT ĐẦU TRAINING NGAY - 3 BƯỚC

## ⚡ Quick Start (20 phút)

### Bước 1: Chuẩn Bị (2 phút)

1. **Zip folder backend:**
   ```bash
   # Trong folder File2Learning/
   # Nén toàn bộ folder backend/ thành backend.zip
   ```

2. **Mở Google Colab:**
   - Truy cập: https://colab.research.google.com/
   - File → New notebook
   - Runtime → Change runtime type → **GPU (T4)**

### Bước 2: Setup Notebook (5 phút)

**Mở file:** `File2Learning_Colab_Ready.txt`

**Copy 26 cells** từ file đó vào Colab theo thứ tự:
- Cell 1: Markdown header
- Cell 2-3: Environment check
- Cell 4-5: **Numpy fix (QUAN TRỌNG!)**
- Cell 6-26: Training pipeline

### Bước 3: Run Training (15 phút)

1. **Chạy Cell 1-5** tuần tự
   
2. **Sau Cell 5:**
   - ⚠️ Runtime → **Restart runtime**
   - Chạy lại Cell 3 (Environment check)
   - **SKIP Cell 5**
   - Tiếp tục từ Cell 7

3. **Cell 11:** Upload `backend.zip` khi được yêu cầu

4. **Cell 19:** Training bắt đầu (~10 phút)

5. **Cell 25:** Download model về

---

## 📋 Checklist

- [ ] Đã zip folder backend → `backend.zip`
- [ ] Đã mở Colab với GPU enabled
- [ ] Đã copy 26 cells vào notebook
- [ ] Đã chạy Cell 5 (Numpy fix)
- [ ] Đã RESTART runtime sau Cell 5
- [ ] Đã skip Cell 5 sau restart
- [ ] Đã upload backend.zip
- [ ] Training đang chạy...
- [ ] Đã download model

---

## 🐛 Troubleshooting Nhanh

### Lỗi: numpy import error
**Fix:** Chạy lại Cell 5 → RESTART runtime → Skip Cell 5

### Lỗi: GPU not available
**Fix:** Runtime → Change runtime type → GPU (T4)

### Lỗi: Files not found
**Fix:** Kiểm tra lại backend.zip có đầy đủ files không

### Lỗi: Out of memory
**Fix:** Cell 15 - Giảm `batch_size: 16` → `8`

---

## 📁 Files Bạn Cần

### 1. File chính để copy vào Colab:
- **`File2Learning_Colab_Ready.txt`** ← Copy 26 cells từ đây

### 2. Files tham khảo (nếu cần):
- `QUICK_FIX_COLAB.txt` - Fix lỗi numpy nhanh
- `FIX_COLAB_ERROR_NOW.md` - Troubleshooting chi tiết
- `COLAB_TRAINING_CELLS_FIXED.py` - Code backup

### 3. File cần upload lên Colab:
- `backend.zip` - Toàn bộ project backend

---

## ⏱️ Timeline Dự Kiến

| Bước | Thời Gian | Mô Tả |
|------|-----------|-------|
| 1. Setup Colab | 2 phút | Tạo notebook, enable GPU |
| 2. Copy cells | 3 phút | Copy 26 cells vào notebook |
| 3. Numpy fix | 1 phút | Cell 5 → Restart runtime |
| 4. Upload files | 2 phút | Upload backend.zip |
| 5. Install deps | 3 phút | Cell 9 - Install packages |
| 6. **Training** | **10 phút** | Cell 19 - Main training |
| 7. Download | 2 phút | Cell 25 - Download model |
| **TỔNG** | **~23 phút** | |

---

## 🎯 Sau Khi Training Xong

### 1. Download Files
Bạn sẽ có file: `file2learning_trained_model.zip`

### 2. Extract & Copy
```bash
# Extract ZIP
unzip file2learning_trained_model.zip

# Copy vào project
cp -r extracted_folder/* backend/models/difficulty_classifier/
```

### 3. Verify
Check các files:
- `best_model.pt` (~250 MB)
- `training_curves.png`
- `confusion_matrix.png`
- `config.json`

### 4. Test Local
```python
from app.ai.models.difficulty_classifier import DifficultyClassifier

classifier = DifficultyClassifier.load_model(
    'models/difficulty_classifier/best_model.pt'
)

result = classifier.predict("Sample text here")
print(f"CEFR Level: {result['level']}")
```

---

## 🚀 Ready?

**Bắt đầu ngay:**
1. Mở `File2Learning_Colab_Ready.txt`
2. Mở Google Colab
3. Copy & Run!

**Cần help?**
- Đọc `FIX_COLAB_ERROR_NOW.md` cho troubleshooting chi tiết
- Kiểm tra output của mỗi cell để debug

---

**Good luck! 🎉**

