# 🎙️ RAG Voice Bot (Public Edition)

Bu repo, **sesli etkileşimli RAG Chatbot** demosudur.  
Kendi sesinle soru sorabilir, dokümanlardan yanıt alabilir ve cevapları **sesli olarak dinleyebilirsin**.  

---

## 📂 Klasör Yapısı
```
RAG-VOICE-BOT-PUBLIC/
├── data/             # Dokümanlar (PDF, DOCX, CSV vs.)
├── voice/            # Ses dosyaları (input.wav, answer.mp3)
├── rag_bot.py        # Ana bot kodu
├── ocr-rag.py        # OCR test/yardımcı script
├── requirements.txt  # Python bağımlılıkları
├── audit.log         # Her sorgu için audit kayıtları
├── out.txt           # Çıktı/test dosyası
├── BACKLOG.txt       # Geliştirme notları (opsiyonel)
└── README.md         # Kurulum & kullanım dökümanı
```

---

## 📑 Desteklenen Dosya Tipleri
- 📄 **PDF** (PyPDF + OCR fallback)  
- 📘 **DOCX** (python-docx)  
- 📊 **XLSX/XLS** (openpyxl)  
- 📑 **CSV** (pandas)  
- 📄 **TXT** (satır bazlı)  
- 📝 **Markdown** (satır bazlı)  
- 🔧 **JSON** (flatten edilmiş)  

---

## 🚀 Kurulum

### 1. API Key’leri Tanımla
```bash
export OPENAI_KEY="senin-openai-key"
export ELEVENLABS_KEY="senin-elevenlabs-key"
export VOICE_ID="senin-elevenlabs-voice-id"
```
👉 İpucu: bunları `~/.zshrc` içine eklersen kalıcı olur.

---

### 2. Sanal Ortam (Önerilir)
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Sistem Bağımlılıkları (macOS)
```bash
brew install poppler
brew install tesseract
brew install tesseract-lang
```

---

### 4. Python Paketleri
```bash
pip install openai chromadb pypdf sentence-transformers sounddevice numpy requests
pip install pytesseract pillow pdf2image python-docx pandas
```

---

### 5. Hugging Face Modelini İndir
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```
➡️ İlk çalıştırmada cache’e kaydolur (`~/.cache/huggingface/`).  
➡️ Sonraki çalıştırmalar çok daha hızlı olur.  

---

### 6. Çalıştırma
📂 `data/` klasörüne test PDF ekle (örn: `SEED.pdf`, `SEED2.pdf`)  

```bash
python rag_bot.py
```

**Akış:**
1. 🎙️ Mikrofon → konuş → sessizlikle otomatik durur.  
2. 📝 Whisper STT → konuşmayı metne çevirir.  
3. 📚 ChromaDB → dokümanlardan bağlam çeker.  
4. 🤖 GPT → yanıt üretir.  
5. 🔊 ElevenLabs → yanıtı sese çevirir → `voice/answer.mp3`.  

👉 Dinlemek için:  
```bash
open voice/answer.mp3
```

---

## 🔥 Özellikler
- 📚 Çoklu PDF desteği  
- 🔍 OCR fallback (taranmış PDF’lerden text çıkarma)  
- ✂️ Satır bazlı chunking (daha hassas arama)  
- 🗂️ Multi-format desteği (PDF, DOCX, XLSX, CSV, TXT, MD, JSON)  
- 💰 Fiyat filtresi (sorguda fiyat, TL, USD, EUR geçerse → sadece fiyat chunk’ları)  
- ⚡ Hızlı embedding modeli: **all-MiniLM-L6-v2**  
- 🎙️ Sessizlikle otomatik ses kaydı bitirme  
- 📜 Audit log (kaynak ve yanıt kaydı)  
- 📂 `data/` klasöründen doküman besleme  
- 🎧 `voice/` klasörüne input/output ses dosyası yazma  
- 🗣️ GPT yanıtlarını günlük konuşma tarzında özetleyerek sunma  

---

## 🔎 Örnek Sorular
**Genel Katalog Soruları**
- “Hangi katalogda daha fazla ürün var?”

**Fiyat Sorguları**
- “1000 TL üzerindeki ürünleri listele.”

---

## 📌 Ek Notlar
- `audit.log` → her sorguyu, kullanılan chunk’ları ve yanıtı kaydeder.  
- Tablo seslendirmeleri bozuk çıkarsa → GPT prompt’unu “cevapları günlük dille özetle” şeklinde ayarlayabilirsin.  
- OCR fallback sadece text olmayan PDF sayfalarında devreye girer.  
- İlk embedding modeli indirme biraz yavaş olabilir (~150 MB). Sonraki çalıştırmalarda hızlıdır.  

---

## 📌 Ekstra: DOCX → PDF Çevirme
```bash
pip install docx2pdf
python -c "from docx2pdf import convert; convert('SEED.docx', 'SEED.pdf')"
```
---

👉 Artık sorularını **sesli sorabilir**, dokümanlardan yanıt alıp dinleyebilirsin 🎧
