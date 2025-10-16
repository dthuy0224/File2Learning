# 📊 Dataset Collection Guide - Difficulty Classification

Tiêu chí và hướng dẫn tìm dataset chất lượng cho training AI model

---

## 🎯 Tiêu Chí Dataset Chất Lượng

### 1. **Minimum Requirements (BẮT BUỘC)**

#### ✅ Size (Kích thước)
```
Minimum:  1,000 samples  (có thể train, accuracy ~75%)
Good:     5,000 samples  (accuracy ~85%)
Excellent: 10,000+ samples (accuracy ~90%+)

Per-label distribution:
- A1: ≥ 150 samples
- A2: ≥ 150 samples  
- B1: ≥ 200 samples (most common level)
- B2: ≥ 200 samples
- C1: ≥ 150 samples
- C2: ≥ 150 samples
```

**Why?** 
- BERT models cần ít nhất 100 examples/class để học patterns
- Balanced dataset → better generalization

---

#### ✅ Labels (Nhãn)
```
REQUIRED: CEFR levels (A1, A2, B1, B2, C1, C2)

Acceptable alternatives:
- Readability scores (Flesch-Kincaid) → convert to CEFR
- Grade levels (Grade 1-12) → map to CEFR
- Lexile scores (200L-1700L) → convert to CEFR

AVOID:
❌ "Easy/Medium/Hard" (too vague)
❌ Unlabeled data (cần manual labeling)
❌ Domain-specific only (medical, legal) → not general
```

**Conversion table:**
```
Grade Level → CEFR
1-2    → A1
3-4    → A2
5-6    → B1
7-8    → B2
9-10   → C1
11-12  → C2

Lexile → CEFR
200-400L   → A1
400-600L   → A2
600-900L   → B1
900-1100L  → B2
1100-1300L → C1
1300L+     → C2
```

---

#### ✅ Quality (Chất lượng content)
```
Good text characteristics:
✅ Natural English (not machine-translated)
✅ Complete sentences
✅ Proper grammar
✅ Clear meaning
✅ Appropriate length (50-500 words/sample)

Red flags:
❌ OCR errors (scanned documents with typos)
❌ Code-switching (mixed languages)
❌ Too short (< 20 words)
❌ Too long (> 1000 words) → hard to label
❌ Machine-generated gibberish
```

---

#### ✅ Diversity (Đa dạng)
```
Topic diversity:
✅ News articles
✅ Stories/narratives
✅ Educational texts
✅ Social media (informal)
✅ Academic papers (formal)
✅ Conversations/dialogues

Genre balance:
- Fiction: 30%
- Non-fiction: 40%
- Academic: 20%
- Informal: 10%

AVOID: Single-domain datasets (all medical, all legal)
```

---

### 2. **Nice-to-Have Features (KHUYẾN NGHỊ)**

#### 🌟 Metadata
```
Useful metadata fields:
- Source (news, textbook, social media)
- Topic/category
- Author information
- Publication date
- Word count
- Readability metrics
- Target audience (kids, adults, professionals)
```

#### 🌟 Pre-processed
```
Ideal format:
{
  "text": "The actual English text...",
  "label": "B1",
  "metadata": {
    "source": "news",
    "topic": "environment",
    "word_count": 250,
    "flesch_score": 65.2
  }
}

Saves time vs raw text files!
```

#### 🌟 Train/Val/Test Splits
```
Pre-split datasets = time saver!

Look for:
- train.json
- val.json  
- test.json

With stratified sampling (balanced labels)
```

---

## 🔍 Recommended Dataset Sources

### **Tier 1: FREE & HIGH-QUALITY** ⭐⭐⭐⭐⭐

#### 1. **OneStopEnglish Corpus**
```
URL: https://github.com/nishkalavallabhi/OneStopEnglishCorpus
Size: 567 texts (189 articles × 3 levels)
Labels: Elementary (A2), Intermediate (B1), Advanced (C1)
Format: Text files
License: CC BY-SA 4.0 (Free for academic)

Pros:
✅ Same article at 3 difficulty levels
✅ News articles (Guardian newspaper)
✅ High quality, manually adapted
✅ Academic research standard

Cons:
⚠️ Only 3 levels (missing A1, B2, C2)
⚠️ All news domain
⚠️ Need manual processing

Download:
git clone https://github.com/nishkalavallabhi/OneStopEnglishCorpus.git
```

---

#### 2. **NewsELA Dataset**
```
URL: https://newsela.com/data/
Size: 1,000+ articles × 5 levels
Labels: Lexile scores → convert to CEFR
Format: HTML/Text
License: Academic use (free with request)

Pros:
✅ 5 reading levels
✅ Large scale
✅ Current news topics
✅ Used in research

Cons:
⚠️ Need to request access
⚠️ Web scraping required
⚠️ Lexile → CEFR conversion needed

Access: Fill form at newsela.com/data
```

---

#### 3. **Cambridge English Corpus**
```
URL: https://www.cambridge.org/gb/cambridgeenglish/
Size: 5,000+ texts with CEFR labels
Labels: Official CEFR (A1-C2) ✅
Format: Various
License: Academic/Research license

Pros:
✅ OFFICIAL CEFR labels (gold standard)
✅ All 6 levels
✅ Exam-quality texts
✅ Multiple genres

Cons:
⚠️ Need to apply for access
⚠️ May have restrictions
⚠️ Not all publicly available

Contact: Cambridge Assessment English
```

---

#### 4. **CEFR-J Corpus (Japanese Learners)**
```
URL: http://www.cefr-j.org/
Size: 2,000+ texts
Labels: CEFR (A1-C2)
Format: Text files
License: Research use

Pros:
✅ CEFR labeled
✅ Educational focus
✅ Free for research

Cons:
⚠️ Focused on Japanese learners
⚠️ May need translation
```

---

#### 5. **CommonLit Corpus**
```
URL: https://www.commonlit.org/
Size: 2,000+ reading passages
Labels: Grade levels (3-12) → convert to CEFR
Format: Web (can scrape)
License: Educational use

Pros:
✅ High-quality educational texts
✅ Various genres
✅ Comprehension questions included
✅ Free for teachers

Cons:
⚠️ Need to scrape/download
⚠️ Grade level → CEFR conversion
```

---

### **Tier 2: GOOD ALTERNATIVES** ⭐⭐⭐⭐

#### 6. **Wikipedia Simple English**
```
URL: https://simple.wikipedia.org/
Size: 200,000+ articles
Labels: Binary (Simple vs Normal)
Format: Wiki dumps
License: CC (Free)

Pros:
✅ Huge dataset
✅ Free & accessible
✅ Easy to download

Cons:
⚠️ Only 2 levels (not full CEFR)
⚠️ Need manual CEFR labeling
⚠️ Quality varies

Use case: Augment dataset with A2 (simple) and C1 (normal)
```

---

#### 7. **Oxford Graded Readers**
```
URL: Various bookstores/libraries
Size: 1,000+ graded books
Labels: Oxford Bookworms levels (1-6)
Format: Books
License: Copyrighted (fair use for research)

Mapping:
Level 1 → A1
Level 2 → A2
Level 3 → B1
Level 4 → B2
Level 5 → C1
Level 6 → C2

Pros:
✅ Perfect CEFR alignment
✅ Engaging stories
✅ Controlled vocabulary

Cons:
⚠️ Copyright issues
⚠️ Need to digitize
⚠️ May need permission
```

---

#### 8. **Project Gutenberg + Readability Scores**
```
URL: https://www.gutenberg.org/
Size: 70,000+ books
Labels: None (need to compute)
Format: Plain text, EPUB
License: Public domain (FREE)

Strategy:
1. Download books
2. Extract passages (500 words)
3. Compute readability (Flesch-Kincaid)
4. Map to CEFR
5. Manual verification

Pros:
✅ Huge, free resource
✅ Classic literature
✅ High-quality writing

Cons:
⚠️ Need to label yourself
⚠️ Time-consuming
⚠️ Older English style
```

---

### **Tier 3: RESEARCH DATASETS** ⭐⭐⭐

#### 9. **Academic Papers with Annotations**
```
Sources:
- Papers With Code (https://paperswithcode.com/)
- ACL Anthology (https://aclanthology.org/)
- Shared Tasks (SemEval, CLEF)

Search keywords:
- "readability assessment dataset"
- "text difficulty corpus"
- "CEFR labeled corpus"
- "graded reading materials"

Pros:
✅ Research-quality
✅ Often pre-split
✅ Benchmarks available

Cons:
⚠️ Smaller sizes
⚠️ Specific domains
⚠️ May need to request
```

---

## 📋 Dataset Evaluation Checklist

### Before Using a Dataset

```
Size & Balance:
[ ] ≥ 1,000 total samples
[ ] ≥ 100 samples per CEFR level
[ ] Not too imbalanced (max 3:1 ratio)

Labels:
[ ] CEFR levels OR convertible (Lexile, Grade)
[ ] Labels are reliable (human-annotated preferred)
[ ] Label distribution documented

Quality:
[ ] Natural English text
[ ] No major OCR errors
[ ] Complete sentences
[ ] Appropriate length (50-500 words)

Diversity:
[ ] Multiple topics/genres
[ ] Not single-domain
[ ] Various text types

Licensing:
[ ] Free for academic use
[ ] No copyright violations
[ ] Proper attribution possible

Format:
[ ] Machine-readable (JSON, CSV, TXT)
[ ] Consistent structure
[ ] UTF-8 encoding
```

---

## 🛠️ DIY Dataset Creation

### If you can't find good dataset...

#### **Option 1: Web Scraping (Legal sources)**

```python
# Example: Scrape graded readers from educational sites
Sources:
- ESL/EFL learning websites
- Educational publishers (with permission)
- Open educational resources

Tools:
- BeautifulSoup (Python)
- Scrapy
- Selenium (for JS-heavy sites)

Legal considerations:
✅ Check robots.txt
✅ Respect rate limits
✅ Only scrape public content
✅ Academic/research use
```

---

#### **Option 2: Manual Labeling**

```
Process:
1. Collect unlabeled texts (Project Gutenberg, news)
2. Use readability formulas (Flesch-Kincaid)
3. Manual review by English teachers
4. Inter-annotator agreement (≥80%)

Tools:
- Flesch-Kincaid calculator
- Textstat (Python library)
- Readable.com

Time estimate: 100 texts/hour with tools
```

---

#### **Option 3: Data Augmentation**

```python
# Expand small dataset
Techniques:
1. Back-translation (EN→FR→EN)
2. Paraphrasing (with GPT)
3. Sentence reordering
4. Synonym replacement (at appropriate level)

Example:
Original (B1): "The government implemented new policies."
Augmented (B1): "New policies were implemented by the government."

Caution: Validate augmented samples!
```

---

## 📊 Recommended Starting Point

### **For File2Learning Project:**

#### **Phase 1: Quick Start (Week 1)**
```
Dataset: OneStopEnglish (567 samples)
+ Synthetic data (current 1,203 samples)
= TOTAL: ~1,770 samples

Expected accuracy: 75-80%
Good enough for: MVP, demo, proof of concept
```

#### **Phase 2: Improve Quality (Week 2-3)**
```
Add: NewsELA (request access)
Add: CommonLit (scrape 1,000 passages)
+ Manual labeling (500 samples from various sources)
= TOTAL: ~3,500 samples

Expected accuracy: 85-87%
Good for: Production, presentation
```

#### **Phase 3: Production Quality (Month 2)**
```
Add: Cambridge Corpus (if access granted)
Add: Manually curated examples (1,000+)
Quality control: Remove low-quality samples
= TOTAL: 5,000-10,000 samples

Expected accuracy: 88-92%
Good for: Publication, commercial use
```

---

## 🎯 Action Plan for You

### **This Week:**

1. **Download OneStopEnglish** (30 minutes)
   ```bash
   git clone https://github.com/nishkalavallabhi/OneStopEnglishCorpus.git
   ```

2. **Process into JSON** (1 hour)
   - Extract texts from folders
   - Label: Ele→A2, Int→B1, Adv→C1
   - Combine with current dataset

3. **Request NewsELA access** (5 minutes)
   - Fill form at newsela.com/data
   - Wait 1-2 weeks for approval

4. **Scrape CommonLit** (2-3 hours)
   - 100-200 passages
   - Grade levels → CEFR

### **Target:** 2,000-2,500 samples by end of week

---

## ⚠️ Common Pitfalls to Avoid

```
❌ DON'T:
1. Use only synthetic data (overfitting)
2. Mix languages (English + others)
3. Include code/formulas in text samples
4. Use auto-translated texts (quality issues)
5. Violate copyrights (paid content)
6. Ignore class imbalance
7. Use texts > 1000 words (hard to label)
8. Mix different labeling standards

✅ DO:
1. Verify label quality (sample check)
2. Balance dataset across levels
3. Include diverse topics
4. Clean text (remove HTML, special chars)
5. Document sources & licenses
6. Split train/val/test properly
7. Manual QA on random samples
8. Track dataset version
```

---

## 📚 Resources & Tools

### **Readability Tools:**
```
Python libraries:
- textstat (Flesch-Kincaid, Gunning Fog, etc.)
- nltk (sentence tokenization)
- spacy (NLP features)

Online calculators:
- readable.com
- readabilityformulas.com
- hemingwayapp.com
```

### **Dataset Processing:**
```python
# Install tools
pip install textstat nltk spacy beautifulsoup4 pandas

# Compute readability
import textstat
text = "Your English text here..."
fk_grade = textstat.flesch_kincaid_grade(text)
flesch_score = textstat.flesch_reading_ease(text)

# Map to CEFR
if fk_grade < 3: level = "A1"
elif fk_grade < 5: level = "A2"
elif fk_grade < 7: level = "B1"
elif fk_grade < 9: level = "B2"
elif fk_grade < 11: level = "C1"
else: level = "C2"
```

---

## 🎓 Academic Standards

If publishing results:
```
Report dataset details:
- Total samples & distribution
- Source & collection method
- Train/val/test split
- Inter-annotator agreement (if manual)
- Baseline metrics (Flesch-Kincaid)
- Any preprocessing applied

Cite properly:
- OneStopEnglish: Vajjala & Lučić (2018)
- NewsELA: Xu et al. (2015)
- Cambridge Corpus: Cambridge Assessment
```

---

## ✅ Summary Checklist

**Minimum viable dataset:**
- [x] 1,000+ samples total
- [x] All 6 CEFR levels represented
- [x] Balanced distribution (150+ per level)
- [x] Natural English text
- [x] Multiple topics/genres
- [x] Clean formatting
- [x] Proper train/val/test split
- [x] Legal to use (free license)

**Start here:** OneStopEnglish + Current synthetic data = ~1,700 samples ✅

**Good enough for:**
- ✅ Training working model
- ✅ Academic project presentation
- ✅ Proof of concept
- ✅ MVP deployment

---

## 🚀 Next Steps

1. **Download OneStopEnglish** → process into JSON
2. **Train with combined dataset** → see improvement
3. **While training:** Request NewsELA, scrape CommonLit
4. **Week 2:** Retrain with larger dataset
5. **Compare results:** Show improvement trajectory

---

**Questions?** Check specific dataset documentation or ask team!

Good luck hunting datasets! 🎯


