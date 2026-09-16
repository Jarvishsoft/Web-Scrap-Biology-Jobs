"""
Biology Matcher
Memvalidasi dan mengklasifikasikan lowongan ke ranah spesialisasi S1 Biologi:
- QA/QC & Food Safety (HACCP / GMP)
- Mikrobiologi & Mikologi
- Bioremediasi & Waste Treatment (WWTP/IPAL)
- Analis Laboratorium & R&D
- Event Job Fair / Walk-in
"""

import re
from typing import List, Tuple
from config import BIOLOGY_RELEVANT_TERMS, BIOLOGY_EXCLUDE_TERMS, BIOLOGY_DOMAINS

def clean_text(text: str) -> str:
    """Membersihkan teks dan mengubah menjadi huruf kecil."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[\r\n\t]+', ' ', text)
    return text.lower()

def is_biology_relevant(title: str, description: str = "", tags: List[str] = None) -> bool:
    """
    Menentukan apakah pekerjaan relevan untuk lulusan Biologi (termasuk QA/QC, Mikrobiologi, WWTP).
    """
    title_clean = clean_text(title)
    desc_clean = clean_text(description)
    tags_clean = " ".join([clean_text(t) for t in (tags or [])])
    full_text = f"{title_clean} {desc_clean} {tags_clean}"

    # Cek kata kunci penolak (exclude) pada judul dan teks
    for exclude_word in BIOLOGY_EXCLUDE_TERMS:
        if exclude_word in title_clean or exclude_word in full_text[:400]:
            return False

    # Deteksi jika pekerjaan adalah IT/Software QA murni
    it_signals = ["selenium", "jmeter", "cypress", "postman", "api testing", "automation framework", "flutter", "react", "bug report", "test case software", "sql query", "fintech", "banking app"]
    if any(sig in full_text for sig in it_signals):
        return False

    # Jika hanya ada kata generik 'qa' atau 'quality assurance' di judul tanpa konteks sains/pangan/lab/farmasi
    is_generic_qa = any(re.search(r'\b' + re.escape(w) + r'\b', title_clean) for w in ["qa", "quality assurance", "qc", "quality control"])
    science_contexts = [
        "food", "pangan", "beverage", "minuman", "farmasi", "pharmaceutical",
        "mikro", "micro", "lab", "laboratorium", "haccp", "gmp", "fssc",
        "iso 22000", "iso 17025", "halal", "organik", "kimia", "chemical",
        "seafood", "daging", "pertanian", "pabrik", "manufaktur", "produksi",
        "sanitasi", "hygiene", "sensori", "bakteri", "wwtp", "ipal", "limbah"
    ]
    if is_generic_qa:
        if not any(ctx in full_text for ctx in science_contexts):
            return False

    # Cek kata kunci biologi pada judul (prioritas tinggi)
    for term in BIOLOGY_RELEVANT_TERMS:
        # Abaikan singkatan generic 'qa' dan 'qc' tanpa konteks
        if term in ["qa", "qc"]:
            continue
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, title_clean):
            return True

    # Jika tidak ada di judul, cek apakah ada di deskripsi atau tags (minimal 2 kemunculan istilah biologi)
    matched_terms = set()
    for term in BIOLOGY_RELEVANT_TERMS:
        if term in ["qa", "qc"]:
            continue
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, full_text):
            matched_terms.add(term)
            if len(matched_terms) >= 2:
                return True

    return False

def classify_biology_field(title: str, description: str = "") -> str:
    """
    Mengelompokkan lowongan ke salah satu bidang spesialisasi kandidat:
    - QA/QC & Food Safety (HACCP/GMP)
    - Mikrobiologi & Mikologi
    - Bioremediasi & Waste Treatment (WWTP/IPAL)
    - Analis Laboratorium & R&D
    - Event Job Fair & Walk-in
    - Biologi Umum
    """
    text_clean = clean_text(f"{title} {description}")

    # Hitung kecocokan tiap domain
    scores = {}
    for domain_key, domain_info in BIOLOGY_DOMAINS.items():
        score = 0
        for term in domain_info["terms"]:
            # Jika ada di judul, bobot 3x
            if term in clean_text(title):
                score += 3
            elif term in text_clean:
                score += 1
        scores[domain_key] = score

    # Ambil domain dengan skor tertinggi
    best_domain = max(scores, key=scores.get)
    if scores[best_domain] > 0:
        return BIOLOGY_DOMAINS[best_domain]["label"]

    return "Biologi & Sains Umum"

def get_matched_biology_keywords(title: str, description: str = "") -> List[str]:
    """Mendapatkan daftar kata kunci biologi/QA/QC/WWTP yang cocok dalam teks."""
    combined = clean_text(f"{title} {description}")
    found = []
    for term in BIOLOGY_RELEVANT_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, combined):
            found.append(term)
    return list(dict.fromkeys(found))[:6]
