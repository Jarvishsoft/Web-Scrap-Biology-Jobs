"""
Location Matcher
Memvalidasi dan mengelompokkan lokasi pekerjaan secara akurat ke dalam
kategori Jakarta, Bekasi/Cikarang, atau sekitarnya.
"""

import re
from typing import Tuple
from config import LOCATIONS_CONFIG

def normalize_location(raw_loc: str) -> str:
    if not raw_loc:
        return ""
    return re.sub(r'[\r\n\t]+', ' ', raw_loc).strip().lower()

def match_location(raw_location: str) -> Tuple[bool, str, str]:
    """
    Mencocokkan string lokasi dengan kamus Jakarta-Bekasi.
    Mengembalikan: (is_matched, category, display_label)
    - category: 'jakarta', 'bekasi', 'jabodetabek_lainnya', atau 'lainnya'
    """
    loc_clean = normalize_location(raw_location)
    if not loc_clean:
        return False, "unknown", "Tidak Diketahui"

    # Cek Bekasi dan Cikarang terlebih dahulu (seringkali ditulis 'Bekasi, Jawa Barat' atau 'Cikarang Utara')
    bekasi_cfg = LOCATIONS_CONFIG["bekasi"]
    for alias in bekasi_cfg["aliases"]:
        if re.search(r'\b' + re.escape(alias) + r'\b', loc_clean):
            return True, "bekasi", bekasi_cfg["label"]

    # Cek Jakarta
    jkt_cfg = LOCATIONS_CONFIG["jakarta"]
    for alias in jkt_cfg["aliases"]:
        if re.search(r'\b' + re.escape(alias) + r'\b', loc_clean):
            return True, "jakarta", jkt_cfg["label"]

    # Cek Jabodetabek lainnya (Tangerang, Depok, Bogor)
    other_cfg = LOCATIONS_CONFIG["jabodetabek_lainnya"]
    for alias in other_cfg["aliases"]:
        if re.search(r'\b' + re.escape(alias) + r'\b', loc_clean):
            return True, "jabodetabek_lainnya", other_cfg["label"]

    return False, "lainnya", raw_location.strip()

def is_jabek_location(raw_location: str, include_surrounding: bool = False) -> bool:
    """Memeriksa apakah lokasi berada di Jakarta atau Bekasi (Jabek)."""
    matched, category, _ = match_location(raw_location)
    if not matched:
        return False
    if category in ["jakarta", "bekasi"]:
        return True
    if include_surrounding and category == "jabodetabek_lainnya":
        return True
    return False
