# PDF için önce pdf2image ile sayfaları resimlere dönüştürmek

from pdf2image import convert_from_path
import pytesseract

# PDF'i resimlere çevir
pages = convert_from_path("ALPCATALOG.pdf", 300)  # 300 DPI
for i, page in enumerate(pages[:2]):  # ilk 2 sayfayı dene
    text = pytesseract.image_to_string(page, lang="tur")
    print(f"Sayfa {i+1} OCR sonucu:\n{text[:500]}")

