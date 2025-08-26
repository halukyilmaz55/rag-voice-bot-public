RAG Voice Bot (Public Edition)

Bu repo, sesli etkileşimli RAG Chatbot demosudur.
Kendi sesinle soru sorabilir, dokümanlardan yanıt alabilir ve cevapları sesli olarak dinleyebilirsin.

Klasör Yapısı

RAG-VOICE-BOT-PUBLIC/
│
├── data/ # Katalog ve diğer dokümanlar (PDF, DOCX, CSV vs.)
├── voice/ # Ses dosyaları (input.wav, answer.mp3)
│
├── rag_bot.py # Ana bot kodu
├── ocr-rag.py # OCR test/yardımcı script
├── requirements.txt # Python bağımlılıkları
├── audit.log # Her sorgu için audit kayıtları
├── out.txt # Çıktı/test dosyası
├── BACKLOG.txt # Geliştirme notları (opsiyonel)
└── README.md # Kurulum & kullanım dökümanı

Desteklenen Dosya Tipleri

PDF (PyPDF + OCR fallback)

DOCX (python-docx)

XLSX/XLS (openpyxl)

CSV (pandas)

TXT (satır bazlı)

Markdown (satır bazlı)

JSON (flatten edilmiş)

Kurulum Öncesi

API Key’leri Tanımla
export OPENAI_KEY="senin-openai-key"
export ELEVENLABS_KEY="senin-elevenlabs-key"
export VOICE_ID="senin-elevenlabs-voice-id"

İstersen bunları ~/.zshrc içine ekleyebilirsin.

Klasör Oluştur
mkdir rag-voice-bot
cd rag-voice-bot

Sanal Ortam (Önerilir)
python3 -m venv venv
source venv/bin/activate

Gerekli Paketler (macOS için)
brew install poppler
brew install tesseract
brew install tesseract-lang

Python paketleri:
pip install openai chromadb pypdf sentence-transformers sounddevice numpy requests
pip install pytesseract pillow pdf2image python-docx pandas

Hugging Face Modelini İndir
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

İlk çalıştırmada cache’e kaydolur (~/.cache/huggingface/).
Sonraki çalıştırmalar çok daha hızlı olur.

Çalışma Klasör Yapısı
rag-voice-bot/
├── data/ (dokümanlar)
├── voice/ (input.wav + answer.mp3)
├── rag_bot.py
└── audit.log

Kod Dosyası
nano rag_bot.py

kod burada olacak

Test için PDF koy
data/SEED.pdf
data/ISILDARCATALOG.pdf

Çalıştır
python rag_bot.py

Akış:

Mikrofon dinler, konuşursun, sessizlikte otomatik durur.

Whisper STT konuşmanı metne çevirir.

ChromaDB ilgili dokümanlardan bağlam getirir.

GPT yanıt üretir.

ElevenLabs yanıtı sese çevirir → voice/answer.mp3

Dinlemek için:
open voice/answer.mp3

Versiyonda Neler Var

Çoklu PDF desteği

OCR fallback (taranmış PDF’lerden text çıkarma)

Satır bazlı chunking (daha hassas arama)

Multi-format dosya desteği (PDF, DOCX, XLSX, CSV, TXT, MD, JSON)

Fiyat filtresi (sorguda fiyat, TL, USD, EUR geçerse sadece fiyat chunk’ları)

Daha hızlı embedding modeli: sentence-transformers/all-MiniLM-L6-v2

Sessizlikle otomatik ses kaydı bitirme

Audit log (her sorgunun kaynak + yanıt kaydı)

data/ klasöründen doküman besleme

voice/ klasörüne input/output dosyalarını yazma

GPT yanıtlarını günlük konuşma tarzında sunma (tablo yerine özetleme opsiyonu)

Örnek Sorular
Genel Katalog Soruları:

Hangi katalogda daha fazla ürün var?

Fiyat Sorguları:

1000 TL üzerindeki ürünleri listele.

Ek Notlar

audit.log her sorguyu, kullanılan chunk’ları ve yanıtı kaydeder.

Tablolar seslendirilirken bozuluyorsa GPT prompt’u “cevapları günlük dille özetle” şeklinde ayarlanabilir.

OCR fallback sadece text olmayan PDF sayfalarında devreye girer.

İlk embedding modeli indirirken yavaş olabilir (~150 MB). Sonraki çalıştırmalarda hızlıdır.

Ekstra: DOCX → PDF Çevirme
pip install docx2pdf
python -c "from docx2pdf import convert; convert('SEED.docx', 'SEED.pdf')"

Artık sesli sorular sorabilir, dokümanlardan yanıt alıp dinleyebilirsin.