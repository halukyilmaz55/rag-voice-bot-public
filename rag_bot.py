"""
Sesli RAG Chatbot Demo v5 (doğal dil + yorumlama + multi-format + fiyat filtresi)
---------------------------------------------------------------------------------
Desteklenen formatlar:
- PDF (PyPDF + OCR fallback)
- DOCX (python-docx)
- XLSX/XLS (openpyxl)
- CSV (pandas)
- TXT (satır bazlı)
- MD (Markdown satır bazlı)
- JSON (dict flatten)

📂 data/   -> dokümanların olduğu klasör
📂 voice/  -> input.wav ve answer.mp3 burada tutulacak
"""

import os, json
import numpy as np
import sounddevice as sd
import wave
from uuid import uuid4
from glob import glob
from pathlib import Path

from openai import OpenAI
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
import chromadb
from chromadb.utils import embedding_functions
import requests
import docx
import pandas as pd

# HuggingFace tokenizer uyarılarını sustur
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Klasörler
DATA_DIR = "data"
VOICE_DIR = "voice"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

# 🔑 API Keys
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
ELEVEN_API_KEY = os.getenv("ELEVENLABS_KEY")
VOICE_ID = os.getenv("VOICE_ID")

if not client.api_key or not ELEVEN_API_KEY or not VOICE_ID:
    raise ValueError("❌ OPENAI_KEY / ELEVENLABS_KEY / VOICE_ID tanımlı değil.")

conversation_history = []


# 🎤 Ses Kaydı (sessizlikle otomatik durur)
def record_until_silence(filename=f"{VOICE_DIR}/input.wav", fs=16000, silence_threshold=0.02, silence_duration=4):
    print("🎤 Konuş, dinleniyor... (susunca otomatik duracak)")
    buffer, silence_counter = [], 0
    chunk = int(0.5 * fs)

    with sd.InputStream(samplerate=fs, channels=1, dtype="float32") as stream:
        while True:
            data, _ = stream.read(chunk)
            buffer.append(data.copy())

            volume = np.linalg.norm(data) / len(data)
            if volume < silence_threshold:
                silence_counter += 0.5
            else:
                silence_counter = 0

            if silence_counter >= silence_duration:
                print("⏹ Sessizlik algılandı, kayıt durdu.")
                break

    audio = np.concatenate(buffer, axis=0)
    audio_int16 = np.int16(audio * 32767)

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(fs)
        wf.writeframes(audio_int16.tobytes())

    print(f"✅ Kayıt alındı: {filename}")
    return filename


# 📝 STT
def speech_to_text(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        tr = client.audio.transcriptions.create(model="whisper-1", file=f)
    print("📝 Kullanıcı dedi ki:", tr.text)
    return tr.text


# 📚 ChromaDB Setup
def setup_chroma():
    chroma = chromadb.PersistentClient(path="chroma_db_v5")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"  # hızlı model
    )
    return chroma.get_or_create_collection("docs", embedding_function=emb_fn)


# 📂 Çoklu dosya ekleme
def add_files_to_chroma(collection, files: list[str]):
    for f in files:
        ext = Path(f).suffix.lower()
        if ext == ".pdf": add_pdf(collection, f)
        elif ext == ".docx": add_docx(collection, f)
        elif ext in [".xlsx", ".xls"]: add_xlsx(collection, f)
        elif ext == ".csv": add_csv(collection, f)
        elif ext == ".txt": add_txt(collection, f)
        elif ext == ".md": add_md(collection, f)
        elif ext == ".json": add_json(collection, f)
        else: print(f"⚠️ {f} desteklenmiyor (skip).")


# --- PDF ---
def add_pdf(collection, pdf_path: str):
    added, reader = 0, PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if not text.strip():  # OCR fallback
            images = convert_from_path(pdf_path, dpi=200, first_page=i+1, last_page=i+1)
            if images: text = pytesseract.image_to_string(images[0], lang="tur+eng")

        for line in text.splitlines():
            if not line.strip(): continue
            is_price = any(sym in line for sym in ["TL", "₺", "USD", "EUR"])
            uid = f"{Path(pdf_path).stem}-{i}-{uuid4().hex[:8]}"
            collection.add(
                documents=[line.strip()],
                ids=[uid],
                metadatas=[{"source": Path(pdf_path).name, "page": i+1, "price": is_price}],
            )
            added += 1
    print(f"📚 {pdf_path}: {added} satır eklendi (PDF + OCR).")


# --- DOCX ---
def add_docx(collection, path: str):
    doc, added = docx.Document(path), 0
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text: continue
        is_price = any(sym in text for sym in ["TL", "₺", "USD", "EUR"])
        uid = f"{Path(path).stem}-{uuid4().hex[:8]}"
        collection.add(
            documents=[text], ids=[uid],
            metadatas=[{"source": Path(path).name, "price": is_price}],
        )
        added += 1
    print(f"📘 {path}: {added} paragraf eklendi (DOCX).")


# --- Excel ---
def add_xlsx(collection, path: str):
    df, added = pd.read_excel(path), 0
    for _, row in df.iterrows():
        text = " | ".join([str(x) for x in row if pd.notna(x)])
        if not text.strip(): continue
        is_price = any(sym in text for sym in ["TL", "₺", "USD", "EUR"])
        uid = f"{Path(path).stem}-{uuid4().hex[:8]}"
        collection.add(
            documents=[text], ids=[uid],
            metadatas=[{"source": Path(path).name, "price": is_price}],
        )
        added += 1
    print(f"📊 {path}: {added} satır eklendi (Excel).")


# --- CSV ---
def add_csv(collection, path: str):
    df, added = pd.read_csv(path), 0
    for _, row in df.iterrows():
        text = " | ".join([str(x) for x in row if pd.notna(x)])
        if not text.strip(): continue
        is_price = any(sym in text for sym in ["TL", "₺", "USD", "EUR"])
        uid = f"{Path(path).stem}-{uuid4().hex[:8]}"
        collection.add(
            documents=[text], ids=[uid],
            metadatas=[{"source": Path(path).name, "price": is_price}],
        )
        added += 1
    print(f"📑 {path}: {added} satır eklendi (CSV).")


# --- TXT / MD ---
def add_txt(collection, path: str):
    added = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            is_price = any(sym in line for sym in ["TL", "₺", "USD", "EUR"])
            uid = f"{Path(path).stem}-{uuid4().hex[:8]}"
            collection.add(
                documents=[line.strip()], ids=[uid],
                metadatas=[{"source": Path(path).name, "price": is_price}],
            )
            added += 1
    print(f"📄 {path}: {added} satır eklendi ({Path(path).suffix.upper()}).")
add_md = add_txt


# --- JSON ---
def add_json(collection, path: str):
    added = 0
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def flatten_json(y, prefix=""):
        out = {}
        if isinstance(y, dict):
            for k, v in y.items(): out.update(flatten_json(v, prefix + k + "."))
        elif isinstance(y, list):
            for i, v in enumerate(y): out.update(flatten_json(v, prefix + str(i) + "."))
        else:
            out[prefix[:-1]] = y
        return out

    flat = flatten_json(data)
    for k, v in flat.items():
        text = f"{k}: {v}"
        is_price = any(sym in str(v) for sym in ["TL", "₺", "USD", "EUR"])
        uid = f"{Path(path).stem}-{uuid4().hex[:8]}"
        collection.add(
            documents=[text], ids=[uid],
            metadatas=[{"source": Path(path).name, "price": is_price}],
        )
        added += 1
    print(f"🔧 {path}: {added} satır eklendi (JSON).")


# --- RAG Query ---
def rag_query(collection, query: str):
    query_lower = query.lower()
    if any(word in query_lower for word in ["fiyat", "tl", "₺", "usd", "eur"]):
        res = collection.query(query_texts=[query], n_results=10, where={"price": True})
    else:
        res = collection.query(query_texts=[query], n_results=15)

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]

    ctx_parts = []
    for d, m in zip(docs, metas):
        if not d: continue
        src = f"{m.get('source','?')}"
        if "page" in m: src += f" s.{m['page']}"
        ctx_parts.append(f"[{src}] {d}")

    return "\n\n".join(ctx_parts), metas


# --- GPT (doğal dil + yorumlama) ---
def generate_answer(query: str, context: str) -> str:
    conversation_history.append({"role": "user", "content": query})
    messages = [{
        "role": "system",
        "content": (
            "Sen bir akıllı asistan gibisin. "
            "Yanıtlarını doğal ve gündelik bir dille ver. "
            "Tabloyu satır satır okuma, onun yerine rakamları özetle ve yorum yap. "
            "Örneğin: '12W Slim LED Panel yaklaşık 150-200 TL, giriş seviyesi uygun bir ürün. "
            "36W model ise 300-400 TL civarında, yani en pahalı seçeneklerden biri.' "
            "Birden fazla ürün varsa fiyat aralıklarını kıyasla. "
            "Her cevabın sonunda mutlaka kaynak dokümanı belirt."
        )
    }]
    messages.extend(conversation_history)
    messages.append({"role": "assistant", "content": f"Bağlam:\n{context}"})

    resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    answer = resp.choices[0].message.content
    print("🤖 Yanıt:", answer)
    conversation_history.append({"role": "assistant", "content": answer})
    return answer


# --- TTS ---
def text_to_speech(text: str, filename=f"{VOICE_DIR}/answer.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
    data = {"text": text}
    r = requests.post(url, headers=headers, json=data); r.raise_for_status()
    with open(filename, "wb") as f: f.write(r.content)
    print(f"🔊 Ses dosyası: {filename}")
    return filename


# --- Audit Log ---
def audit_log(query: str, context: str, answer: str, metas: list):
    with open("audit.log", "a", encoding="utf-8") as f:
        f.write("\n=== Yeni Sorgu ===\n")
        f.write(f"📝 Kullanıcı: {query}\n")
        fiyat_mode = any(word in query.lower() for word in ["fiyat","tl","₺","usd","eur"])
        f.write(f"🔎 Arama parametresi: {'fiyat filtresi aktif' if fiyat_mode else 'genel sorgu'}\n")
        f.write(f"📊 Chunk sayısı: {len(metas)}\n")
        f.write("📂 Kaynaklar:\n")
        for m in metas:
            src = m.get("source","?")
            page = m.get("page","?")
            f.write(f" - {src} s.{page}\n")
        f.write(f"🤖 Yanıt: {answer}\n")
        f.write("=================\n")


# --- Main ---
if __name__ == "__main__":
    file_list = sorted(glob(f"{DATA_DIR}/*.*"))
    file_list = [f for f in file_list if Path(f).suffix.lower() in 
                 [".pdf",".docx",".xlsx",".xls",".csv",".txt",".md",".json"]]

    if not file_list:
        print("⚠️ data/ klasöründe uygun dosya yok.")
    else:
        print("🗂️ Eklenecek dosyalar:", ", ".join(file_list))

    wav = record_until_silence()
    query = speech_to_text(wav)

    coll = setup_chroma()
    if file_list: add_files_to_chroma(coll, file_list)

    context, metas = rag_query(coll, query)
    answer = generate_answer(query, context)
    audit_log(query, context, answer, metas)
    text_to_speech(answer)
