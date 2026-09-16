"""
Biology Matcher
Memvalidasi dan mengklasifikasikan lowongan KHUSUS UNTUK JURUSAN BIOLOGI:
1. QA/QC & Food Safety (HACCP/GMP)
2. Mikrobiologi & Mikologi
3. Bioremediasi & Waste Treatment (WWTP/IPAL)
4. Analis Laboratorium & R&D

DILARANG KERAS:
- Segala bentuk jurusan TEKNIK (Mesin, Elektro, Sipil, Industri, Lingkungan, Kimia)
  KECUALI jika lowongan tersebut secara eksplisit juga menerima lulusan BIOLOGI / BIOTEKNOLOGI.
- Posisi kuliner/dapur (Chef, Cook, Restoran), Mebel/Kayu, Tekstil/Garmen, PPIC, IT Software, dan Pengajar/Guru.
"""

import re
from typing import List
from config import BIOLOGY_EXCLUDE_TERMS, BIOLOGY_DOMAINS

# 1. Istilah Inti Biologi & Biosains (Lolos afirmatif jika ada di judul)
CORE_BIO_TERMS = [
    "biologi", "biology", "s1 biologi", "mikrobiologi", "microbiology",
    "bioteknologi", "biotechnology", "mikologi", "mycology",
    "kultur jaringan", "tissue culture", "biosains", "bioscience",
    "ilmu hayati", "life science", "life sciences", "bioremediasi", "bioremediation",
    "botani", "zoologi", "biokimia", "biochemistry"
]

# 2. Jurusan Rekayasa / Teknik yang Mendiskualifikasi jika Tidak Menerima Biologi
DISQUALIFYING_ENGINEERING_MAJORS = [
    "teknik mesin", "mechanical engineering",
    "teknik elektro", "electrical engineering",
    "teknik industri", "industrial engineering",
    "teknik sipil", "civil engineering",
    "teknik lingkungan", "environmental engineering",
    "teknik kimia", "chemical engineering",
    "teknik informatika", "computer science",
    "petroleum", "perminyakan",
    "metallurgy", "metalurgi",
    "pertambangan", "mining",
    "arsitektur", "architecture",
    "tata boga", "culinary arts", "perhotelan"
]

# 3. Jurusan Biologi / Sains Hayati yang Wajib Ada Jika Ada Syarat Jurusan Teknik
ACCEPTED_BIO_MAJORS = [
    "biologi", "biology", "s1 biologi",
    "bioteknologi", "biotechnology",
    "mikrobiologi", "microbiology",
    "biosains", "bioscience",
    "sains hayati", "ilmu hayati", "life science", "life sciences",
    "mipa", "sains", "ilmu pengetahuan alam"
]

# 4. Judul Fungsional di 4 Ranah Peminatan Biologi
TARGET_DOMAIN_ROLES = [
    # QA/QC & Food Safety
    "qc", "qa", "quality control", "quality assurance", "food safety",
    "haccp", "gmp", "inspeksi mutu", "fssc", "cppob", "cpob",
    # Bioremediasi & WWTP/IPAL
    "wwtp", "ipal", "bioremediasi", "waste treatment", "pengolahan limbah",
    "water treatment", "analis limbah", "analis lingkungan",
    # Analis Lab & R&D
    "analis laboratorium", "laboratory analyst", "analis lab", "teknisi lab",
    "r&d", "research and development", "scientist", "formulator", "laboratorium",
    "laboratory", "lab", "technologist", "medical laboratory"
]

# 5. Sinyal Konteks Sains / Laboratorium / Pangan / Hayati yang Sah
VALID_SCIENCE_SIGNALS = ACCEPTED_BIO_MAJORS + [
    "uji mikrobiologi", "analisis mikrobiologi", "pengujian mikrobiologi",
    "kultur mikroba", "bakteri", "bakteriologi", "yeast", "khamir", "kapang", "jamur",
    "cawan petri", "media agar", "coliform", "salmonella", "angka lempeng total", "alt",
    "sterilisasi aseptis", "teknik aseptis", "autoclave", "pcr", "elisa",
    "spektrofotometer", "food", "pangan", "beverage", "farmasi", "pharmaceutical",
    "kosmetik", "cosmetic", "bio-treatment", "lumpur aktif", "degradasi biologis",
    "aerob", "anaerob", "kualitas air", "sanitasi", "hygiene", "sensori", "organoleptik",
    "haccp", "gmp", "fssc 22000", "iso 22000", "iso 17025", "cppob", "cpob",
    "kimia", "analis kimia", "food technologist"
]

def clean_text(text: str) -> str:
    """Membersihkan teks dan mengubah menjadi huruf kecil."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[\r\n\t]+', ' ', text)
    return text.lower().strip()

def is_biology_relevant(title: str, description: str = "", tags: List[str] = None) -> bool:
    """
    Menentukan apakah pekerjaan BENAR-BENAR relevan KHUSUS LULUSAN BIOLOGI SAJA.
    Aturan Keras:
    1. Menolak kata kunci negatif judul (Chef, Furniture, Mesin, Sipil, PPIC, Guru, IT).
    2. Menolak posisi yang mensyaratkan jurusan TEKNIK apapun tanpa membuka untuk Biologi.
    3. Menerima pekerjaan dari 4 ranah: QA/QC Food Safety, Mikrobiologi, WWTP/Bioremediasi, dan Analis Lab & R&D.
    """
    title_clean = clean_text(title)
    desc_clean = clean_text(description)
    tags_clean = " ".join([clean_text(t) for t in (tags or [])])
    full_text = f"{title_clean} {desc_clean} {tags_clean}"

    # ── 1. CEK KATA KUNCI PENOLAK KERAS PADA JUDUL ──
    for exclude_word in BIOLOGY_EXCLUDE_TERMS:
        if re.search(r'\b' + re.escape(exclude_word) + r'\b', title_clean):
            return False

    # ── 2. CEK JUDUL TEKNIK / ENGINEERING MURNI ──
    # Jika ada kata 'engineer', 'engineering', atau 'teknik' di judul,
    # HANYA izinkan jika bersangkutan langsung dengan mikrobiologi/bioteknologi
    if re.search(r'\b(engineer|engineering|teknik)\b', title_clean):
        has_bio_engineer = any(b in title_clean for b in ["microbiol", "mikrobiol", "biotech", "biotek", "genet", "biolog"])
        if not has_bio_engineer:
            return False

    # ── 3. FILTER KHUSUS: ANALIS KIMIA MURNI TANPA KONTEKS BIOLOGI/PANGAN/MIKRO ──
    if re.search(r'\b(analis kimia|analis laboratorium kimia|chemist|chemistry)\b', title_clean):
        has_bio_context = any(b in full_text for b in ["biolog", "mikro", "biokim", "pangan", "food", "farmasi", "pharmaceut", "bakteri", "yeast", "haccp", "gmp"])
        if not has_bio_context:
            return False

    # ── 4. FILTER JURUSAN: JANGAN MASUKKAN TEKNIK APAPUN ITU ──
    # Jika deskripsi mensyaratkan jurusan teknik (mesin, elektro, sipil, industri, lingkungan, kimia)
    # Wajib dicek apakah jurusan Biologi / Bioteknologi / Sains Hayati juga diterima.
    # Jika hanya untuk jurusan teknik murni tanpa biologi -> TOLAK!
    has_eng_major = any(em in full_text for em in DISQUALIFYING_ENGINEERING_MAJORS)
    if has_eng_major:
        has_bio_major = any(bm in full_text for bm in ACCEPTED_BIO_MAJORS)
        if not has_bio_major:
            return False

    # ── 4. VALIDASI AFIRMATIF BIOLOGI (4 RANAH UTAMA) ──

    # Kondisi A: Judul pekerjaan secara eksplisit menyebutkan keilmuan biologi inti
    for bio in CORE_BIO_TERMS:
        if re.search(r'\b' + re.escape(bio) + r'\b', title_clean):
            return True

    # Kondisi B: Judul adalah peran fungsional di 4 ranah target
    # (QA/QC Food Safety, Mikrobiologi, WWTP/IPAL Biologis, Analis Lab & R&D)
    is_target_role = any(re.search(r'\b' + re.escape(r) + r'\b', title_clean) for r in TARGET_DOMAIN_ROLES)
    if is_target_role:
        # Wajib memiliki konteks sains hayati, biologi, pangan, farmasi, atau laboratorium yang valid
        has_science_signal = any(re.search(r'\b' + re.escape(sig) + r'\b', full_text) for sig in VALID_SCIENCE_SIGNALS)
        if has_science_signal:
            return True

    # Jika tidak memenuhi Kondisi A maupun Kondisi B -> TOLAK
    return False

def classify_biology_field(title: str, description: str = "") -> str:
    """
    Mengelompokkan lowongan ke salah satu dari 4 sub-bidang Biologi resmi:
    - QA/QC & Food Safety (HACCP/GMP)
    - Mikrobiologi & Mikologi
    - Bioremediasi & Waste Treatment (WWTP/IPAL)
    - Analis Laboratorium & R&D
    """
    text_clean = clean_text(f"{title} {description}")

    scores = {}
    for domain_key, domain_info in BIOLOGY_DOMAINS.items():
        score = 0
        for term in domain_info["terms"]:
            if term in clean_text(title):
                score += 5
            elif term in text_clean:
                score += 1
        scores[domain_key] = score

    best_domain = max(scores, key=scores.get)
    if scores[best_domain] > 0:
        return BIOLOGY_DOMAINS[best_domain]["label"]

    if any(m in clean_text(title) for m in ["mikro", "micro", "jamur", "yeast"]):
        return "Mikrobiologi & Mikologi"
    if any(w in clean_text(title) for w in ["wwtp", "ipal", "waste", "limbah", "bioremed"]):
        return "Bioremediasi & Waste Treatment (WWTP/IPAL)"
    if any(q in clean_text(title) for q in ["qa", "qc", "food", "safety", "haccp", "gmp"]):
        return "QA/QC & Food Safety (HACCP/GMP)"

    return "Analis Laboratorium & R&D"

def get_matched_biology_keywords(title: str, description: str = "") -> List[str]:
    """Mendapatkan daftar kata kunci biologi yang cocok dalam teks lowongan."""
    combined = clean_text(f"{title} {description}")
    candidates = CORE_BIO_TERMS + [
        "haccp", "gmp", "fssc 22000", "iso 22000", "iso 17025", "cppob", "cpob",
        "keamanan pangan", "wwtp", "ipal", "pengolahan limbah", "lumpur aktif",
        "uji mikrobiologi", "alt", "coliform", "salmonella", "bakteri",
        "r&d", "analis laboratorium", "pcr", "elisa"
    ]
    found = []
    for term in candidates:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, combined):
            found.append(term)
    return list(dict.fromkeys(found))[:5]
