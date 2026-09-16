"""
Konfigurasi Terpusat untuk Web Scraper Lowongan Kerja Biologi Fresh Graduate
Khusus S1 Biologi (Target: QA/QC & Food Safety, HACCP & GMP, Mikrobiologi, Mikologi, Bioremediasi & WWTP)
Fokus Wilayah: Jakarta & Bekasi (Jabek / Cikarang / Kawasan Industri Terkait)
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Kata Kunci Pencarian Khusus S1 Biologi (Fresh Graduate)
# Disesuaikan secara presisi dengan keahlian:
# 1. QA/QC & Food Safety (Pangan, Minuman, Farmasi, Kosmetik)
# 2. HACCP & GMP (FSSC 22000, ISO 22000, CPPOB)
# 3. Mikrobiologi (Pengujian mikrobiologi, ALT, Coliform, sterilisasi)
# 4. Mikologi (Fungi, kapang, khamir, jamur, fermentasi)
# 5. Bioremediasi & Waste Treatment (WWTP, IPAL, analisis limbah, bio-treatment)
# 6. Analis Laboratorium & R&D
BIOLOGY_KEYWORDS = [
    # QA/QC & Food Safety
    "qa food safety",
    "qc food safety",
    "quality assurance pangan",
    "quality control pangan",
    "food safety specialist",
    "qc inspector pangan",
    
    # HACCP & GMP
    "haccp",
    "gmp",
    "fssc 22000",
    "cppob",
    "cpob",
    
    # Mikrobiologi & Mikologi
    "mikrobiologi",
    "microbiology",
    "analis mikrobiologi",
    "microbiology analyst",
    "mikologi",
    "mycology",
    "fermentasi",
    
    # Bioremediasi & Waste Treatment
    "bioremediasi",
    "bioremediation",
    "waste treatment biologi",
    "wwtp",
    "ipal",
    "water treatment analyst",
    "pengolahan limbah",
    "analis lingkungan",
    
    # Laboratorium & Biologi Umum
    "analis laboratorium",
    "laboratory analyst",
    "biologi",
    "biology",
    "bioteknologi",
    "assistant scientist microbiology",
    
    # Event & Walk-in
    "job fair biologi",
    "walk in interview qc"
]

# Kamus Relevansi Biologi (Untuk verifikasi konten dan penentuan kategori bidang)
BIOLOGY_DOMAINS = {
    "qa_qc_food_safety": {
        "label": "QA/QC & Food Safety (HACCP/GMP)",
        "terms": [
            "qa", "qc", "quality assurance", "quality control", "food safety",
            "haccp", "gmp", "fssc 22000", "iso 22000", "cppob", "cpob",
            "keamanan pangan", "sensori", "organoleptik", "hygiene", "sanitasi",
            "inspeksi mutu", "spesifikasi bahan", "retensi sampel"
        ]
    },
    "microbiology_mycology": {
        "label": "Mikrobiologi & Mikologi",
        "terms": [
            "mikrobiologi", "microbiology", "mikroba", "bakteri", "bakteriologi",
            "mikologi", "mycology", "jamur", "fungi", "yeast", "khamir", "kapang",
            "fermentasi", "kultur mikroba", "media agar", "cawan petri", "alt",
            "angka lempeng total", "coliform", "salmonella", "e. coli", "autoclave",
            "aseptis", "sterilisasi", "inkubator", "gram staining", "pewarnaan gram"
        ]
    },
    "bioremediation_waste": {
        "label": "Bioremediasi & Waste Treatment (WWTP/IPAL)",
        "terms": [
            "bioremediasi", "bioremediation", "waste treatment", "wwtp", "ipal",
            "pengolahan limbah", "limbah cair", "sludge", "lumpur aktif", "bod",
            "cod", "tss", "do meter", "aerob", "anaerob", "kualitas air",
            "lingkungan", "amdal", "b3", "bio-treatment", "degradasi biologis"
        ]
    },
    "lab_rnd": {
        "label": "Analis Laboratorium & R&D",
        "terms": [
            "analis laboratorium", "laboratory analyst", "lab tech", "teknisi lab",
            "r&d", "research and development", "bioteknologi", "biotechnology",
            "pcr", "elisa", "spektrofotometer", "kromatografi", "titrasi",
            "preparasi sampel", "iso 17025", "reagen", "bahan kimia"
        ]
    },
    "job_fair_event": {
        "label": "Event Job Fair & Walk-in",
        "terms": [
            "job fair", "career expo", "bursa kerja", "walk in interview",
            "walk-in interview", "festival karier"
        ]
    }
}

# Seluruh kata kunci biologi gabungan
BIOLOGY_RELEVANT_TERMS = []
for domain in BIOLOGY_DOMAINS.values():
    BIOLOGY_RELEVANT_TERMS.extend(domain["terms"])
BIOLOGY_RELEVANT_TERMS = list(dict.fromkeys(BIOLOGY_RELEVANT_TERMS))

# Kata Kunci Penolak (False Positives seperti IT/Software QA, Developer, Sales, Driver)
BIOLOGY_EXCLUDE_TERMS = [
    "software qa", "software quality", "software engineer", "frontend", "backend",
    "full stack", "fullstack", "devops", "qa engineer", "qa tester", "qa manual",
    "qa automation", "automation tester", "test engineer", "sqa", "it quality assurance",
    "quality assurance engineer", "quality assurance tester", "automation test",
    "sales motor", "sales mobil", "driver", "kurir", "satpam", "security guard",
    "telemarketing", "call center", "accounting tax", "pajak", "audit keuangan",
    "civil engineer", "arsitek bangunan", "mechanical technician motor", "bengkel"
]

# Kamus Lokasi Jakarta & Bekasi (Jabek)
LOCATIONS_CONFIG = {
    "jakarta": {
        "label": "Jakarta",
        "aliases": [
            "jakarta", "dki jakarta", "jakarta pusat", "jakarta selatan",
            "jakarta barat", "jakarta timur", "jakarta utara", "central jakarta",
            "south jakarta", "west jakarta", "east jakarta", "north jakarta",
            "area dki jakarta", "jakarta raya"
        ]
    },
    "bekasi": {
        "label": "Bekasi / Cikarang",
        "aliases": [
            "bekasi", "kota bekasi", "kabupaten bekasi", "kab. bekasi",
            "cikarang", "cikarang utara", "cikarang barat", "cikarang selatan",
            "cikarang pusat", "cikarang timur", "jababeka", "mm2100",
            "ejip", "giic", "delta silicon", "tambun", "cibitung"
        ]
    },
    "jabodetabek_lainnya": {
        "label": "Jabodetabek Sekitarnya",
        "aliases": [
            "tangerang", "tangerang selatan", "tangsel", "depok",
            "bogor", "karawang", "serang"
        ]
    }
}

# Kriteria Fresh Graduate
FRESHGRAD_POSITIVE_TERMS = [
    "fresh graduate", "fresh graduates", "freshgraduate", "lulusan baru",
    "entry level", "entry-level", "tanpa pengalaman", "no experience",
    "0-1 tahun", "0 - 1 tahun", "0-2 tahun", "0 - 2 tahun", "1 tahun",
    "1 year", "less than 1 year", "minimal s1", "s1 biologi", "s1 kimia",
    "terbuka untuk lulusan baru", "tidak berpengalaman", "junior", "trainee",
    "internship", "magang", "asisten"
]

# User-Agent Header Standar Browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

# Request delay (detik) antar request
REQUEST_DELAY = 1.0
