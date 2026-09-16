"""
CSV and JSON Exporter
Mengekspor data lowongan kerja ke format CSV dan JSON dengan penamaan kolom Indonesia yang ramah.
"""

import csv
import json
import datetime
from pathlib import Path
from typing import List
import pandas as pd

from scrapers.base_scraper import JobItem

def export_to_csv(jobs: List[JobItem], output_path: Path) -> Path:
    """Mengekspor daftar lowongan ke file CSV UTF-8 dengan header bahasa Indonesia."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    target_path = output_path

    # Format data dengan nama kolom yang ramah dibaca manusia
    formatted_records = []
    for j in jobs:
        if j.city_category == "bekasi":
            area_str = "Bekasi / Cikarang"
        elif j.city_category == "jakarta":
            area_str = "Jakarta"
        else:
            area_str = "Jabodetabek Sekitarnya"

        formatted_records.append({
            "Posisi_Lowongan": j.title,
            "Nama_Perusahaan": j.company,
            "Kota_Area": area_str,
            "Lokasi_Spesifik": j.location,
            "Fokus_Bidang": j.field_category,
            "Skill_Kesesuaian": ", ".join(j.matched_keywords) if j.matched_keywords else "-",
            "Tingkat_Pengalaman": j.experience_level,
            "Estimasi_Gaji": j.salary,
            "Portal_Sumber": j.source,
            "Tanggal_Posting": j.posted_at or "Baru",
            "Link_Lamaran": j.apply_url
        })

    def _write_csv(path_to_write: Path):
        if formatted_records:
            df = pd.DataFrame(formatted_records)
            df.to_csv(path_to_write, index=False, encoding='utf-8-sig')
        else:
            with open(path_to_write, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Posisi_Lowongan", "Nama_Perusahaan", "Kota_Area", "Fokus_Bidang", "Link_Lamaran"])

    try:
        _write_csv(target_path)
    except PermissionError:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")
        _write_csv(fallback_path)
        print(f"[Peringatan] File {output_path.name} sedang dibuka oleh program lain. Tersimpan sebagai: {fallback_path.name}")
        return fallback_path

    return target_path

def export_to_json(jobs: List[JobItem], output_path: Path) -> Path:
    """Mengekspor daftar lowongan ke file JSON berindentasi rapi."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    target_path = output_path

    records = [job.to_dict() for job in jobs]

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except PermissionError:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")
        with open(fallback_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"[Peringatan] File {output_path.name} sedang dibuka. Tersimpan sebagai: {fallback_path.name}")
        return fallback_path

    return target_path
