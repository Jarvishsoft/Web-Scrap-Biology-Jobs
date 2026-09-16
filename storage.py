"""
Storage & Data Manager
Mengelola penyimpanan persisten data lowongan, penggabungan data lama + data baru (incremental append),
serta deduplikasi agar data lama tidak hilang saat proses scraping berulang kali dijalankan.
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

from config import OUTPUT_DIR
from scrapers.base_scraper import JobItem
from exporters import export_to_excel, export_to_csv, export_to_json, export_to_dashboard

MASTER_JSON_PATH = OUTPUT_DIR / "lowongan_biologi_jabek.json"

def _clean_str(text: str) -> str:
    """Membersihkan dan menormalisasi teks untuk perbandingan."""
    if not text:
        return ""
    # Hapus karakter non-alphanumeric dan ubah ke lowercase
    return re.sub(r"[^a-zA-Z0-9]", "", text.lower())

def get_job_dedup_keys(job: JobItem) -> List[str]:
    """Menghasilkan kunci unik deduplikasi untuk sebuah JobItem."""
    keys = []
    
    # 1. Kunci URL (tanpa parameter query)
    url = (job.apply_url or "").strip()
    if url:
        clean_url = url.split("?")[0].rstrip("/").lower()
        keys.append(f"url:{clean_url}")

    # 2. Kunci ID platform (misal li-4464439913)
    job_id = (job.id or "").strip()
    if job_id:
        keys.append(f"id:{job_id.lower()}")

    # 3. Kunci Judul + Perusahaan (dibersihkan dari spasi/simbol)
    norm_title = _clean_str(job.title)
    norm_comp = _clean_str(job.company)
    if norm_title and norm_comp:
        keys.append(f"tc:{norm_title}___{norm_comp}")

    return keys

def load_stored_jobs(file_path: Path = MASTER_JSON_PATH) -> List[JobItem]:
    """Memuat lowongan yang sebelumnya tersimpan dari file JSON master."""
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            return []

        jobs: List[JobItem] = []
        from filters.biology_matcher import is_biology_relevant, classify_biology_field
        for item in raw_data:
            if not isinstance(item, dict) or not item.get("title"):
                continue

            title = str(item.get("title", ""))
            description = str(item.get("description", ""))

            # Filter ketat: Hanya masukkan lowongan khusus jurusan Biologi
            if not is_biology_relevant(title, description):
                continue

            # Perbarui kategori bidang ke 4 ranah spesialisasi biologi resmi
            field_category = str(item.get("field_category", ""))
            if not field_category or field_category in ("Biologi Umum", "Biologi & Sains Umum", "Analis Laboratorium & Bioteknologi"):
                field_category = classify_biology_field(title, description)

            jobs.append(JobItem(
                id=str(item.get("id", "")),
                title=title,
                company=str(item.get("company", "")),
                location=str(item.get("location", "")),
                city_category=str(item.get("city_category", "jabodetabek_lainnya")),
                is_fresh_graduate=bool(item.get("is_fresh_graduate", True)),
                experience_level=str(item.get("experience_level", "Fresh Graduate / Entry Level")),
                salary=str(item.get("salary", "Sesuai Kebijakan Perusahaan")),
                description=description,
                field_category=field_category,
                matched_keywords=list(item.get("matched_keywords", [])),
                apply_url=str(item.get("apply_url", item.get("url", ""))),
                posted_at=str(item.get("posted_at", item.get("posted_date", "Tersedia"))),
                source=str(item.get("source", ""))
            ))
        return jobs
    except Exception as e:
        print(f"[Warning] Gagal memuat lowongan tersimpan: {e}")
        return []

def merge_and_append_jobs(existing_jobs: List[JobItem], new_jobs: List[JobItem]) -> Tuple[List[JobItem], int]:
    """
    Menggabungkan lowongan baru ke dalam daftar lowongan lama secara inkremental (APPEND).
    - Data lama TIDAK AKAN PERNAH DIHAPUS / DIGANTIKAN.
    - Lowongan yang sudah ada diperbarui infonya jika ditemukan kembali (misal tanggal posting / gaji / link).
    - Lowongan yang benar-benar baru dimasukkan ke posisi paling atas agar langsung terlihat.
    - Lowongan lama yang tidak muncul pada scraping kali ini tetap aman dipertahankan.
    
    Mengembalikan:
        (daftar_semua_lowongan_gabungan, jumlah_lowongan_baru_yang_ditambahkan)
    """
    key_to_job: Dict[str, JobItem] = {}
    ordered_jobs: List[JobItem] = []

    # 1. Daftarkan seluruh data lama ke dictionary lookup
    for job in existing_jobs:
        keys = get_job_dedup_keys(job)
        # Cegah duplikasi internal di data lama itu sendiri
        if not any(k in key_to_job for k in keys):
            ordered_jobs.append(job)
            for k in keys:
                key_to_job[k] = job

    brand_new_jobs: List[JobItem] = []

    # 2. Periksa lowongan baru satu per satu (HANYA lowongan khusus jurusan Biologi)
    from filters.biology_matcher import is_biology_relevant
    for new_job in new_jobs:
        if not is_biology_relevant(new_job.title, new_job.description):
            continue
        keys = get_job_dedup_keys(new_job)
        matched_existing: JobItem = None
        
        for k in keys:
            if k in key_to_job:
                matched_existing = key_to_job[k]
                break

        if matched_existing:
            # Lowongan sudah pernah ada sebelumnya: update data jika ada info yang lebih lengkap
            if new_job.apply_url and not matched_existing.apply_url:
                matched_existing.apply_url = new_job.apply_url
            if new_job.salary and new_job.salary != "Sesuai Kebijakan Perusahaan":
                matched_existing.salary = new_job.salary
            if new_job.posted_at and new_job.posted_at not in ("Tersedia", "Baru"):
                matched_existing.posted_at = new_job.posted_at
            if new_job.description and len(new_job.description) > len(matched_existing.description or ""):
                matched_existing.description = new_job.description
            # Pastikan kunci-kunci baru dari new_job juga memetakan ke job yang sudah ada
            for k in keys:
                key_to_job[k] = matched_existing
        else:
            # Lowongan benar-benar baru!
            brand_new_jobs.append(new_job)
            for k in keys:
                key_to_job[k] = new_job

    # Letakkan lowongan baru di urutan paling atas agar mudah dilihat pengguna
    final_jobs = brand_new_jobs + ordered_jobs
    return final_jobs, len(brand_new_jobs)

def save_all_job_data(jobs: List[JobItem]) -> dict:
    """
    Menyimpan daftar seluruh lowongan ke semua format keluaran (Excel, CSV, JSON, HTML Dashboard).
    Semua nama file sinkron otomatis.
    """
    excel_path = OUTPUT_DIR / "lowongan_biologi_jabek.xlsx"
    csv_path   = OUTPUT_DIR / "lowongan_biologi_jabek.csv"
    json_path  = OUTPUT_DIR / "lowongan_biologi_jabek.json"
    html_path  = OUTPUT_DIR / "dashboard.html"

    res_excel = export_to_excel(jobs, excel_path)
    res_csv   = export_to_csv(jobs, csv_path)
    res_json  = export_to_json(jobs, json_path)
    res_html  = export_to_dashboard(jobs, html_path)

    return {
        "excel": res_excel,
        "csv": res_csv,
        "json": res_json,
        "html": res_html,
        "total": len(jobs)
    }
