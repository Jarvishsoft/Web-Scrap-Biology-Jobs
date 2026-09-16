"""
Fresh Graduate Matcher
Memvalidasi apakah lowongan ramah untuk pelamar Fresh Graduate / Entry-Level.
"""

import re
from config import FRESHGRAD_POSITIVE_TERMS

# Syarat pengalaman tinggi yang langsung menolak status fresh graduate murni
HIGH_EXP_PATTERNS = [
    r'(?:minimal|pengalaman|experience)\s*(?:setidaknya)?\s*([3-9]|\d{2})\s*(?:tahun|thn|year|years)',
    r'(?:minimal|min\.?)\s*([3-9]|\d{2})\s*tahun',
    r'senior\s+(?:analyst|scientist|manager|supervisor)',
    r'lead\s+(?:microbiologist|technician|qc)'
]

def is_freshgraduate_friendly(
    title: str = "",
    description: str = "",
    experience_level_field: str = "",
    is_explicit_freshgrad: bool = None
) -> bool:
    """
    Menentukan apakah posisi dapat dilamar oleh Fresh Graduate.
    """
    # Jika API portal (seperti Kalibrr) sudah eksplisit menandai isOpenToFreshGrads
    if is_explicit_freshgrad is True:
        return True

    text_combined = f"{title} {description} {experience_level_field}".lower()

    # Cek apakah judul mengandung 'Senior', 'Manager', 'Lead', 'Head'
    if re.search(r'\b(senior|mgr|manager|head|lead|supervisor|spv)\b', title.lower()):
        return False

    # Cek apakah mensyaratkan pengalaman di atas 2 tahun
    for pattern in HIGH_EXP_PATTERNS:
        if re.search(pattern, text_combined):
            return False

    # Cek tanda positif fresh graduate
    if is_explicit_freshgrad is not None and is_explicit_freshgrad is False:
        # Jika portal secara eksplisit menyatakan false tapi teks mengandung junior / 0-1 thn
        for term in FRESHGRAD_POSITIVE_TERMS:
            if re.search(r'\b' + re.escape(term) + r'\b', text_combined):
                return True
        return False

    # Jika field experience level bertuliskan 'Entry level', 'Associate', atau 'Not Applicable'
    if experience_level_field:
        exp_low = experience_level_field.lower()
        if any(e in exp_low for e in ["entry", "pemula", "tidak berlaku", "not applicable", "intern", "magang"]):
            return True

    # Cek kata kunci fresh graduate pada teks
    for term in FRESHGRAD_POSITIVE_TERMS:
        if re.search(r'\b' + re.escape(term) + r'\b', text_combined):
            return True

    # Jika judul posisi bertipe Junior / Assistant / Operator / Technologist tanpa syarat exp berat,
    # biasanya ditujukan untuk lulusan baru
    if re.search(r'\b(junior|assistant|asisten|technologist|teknisi|operator|staff|staf)\b', title.lower()):
        return True

    return True  # Default inklusif jika tidak ditemukan batasan pengalaman tinggi
