"""
Kalibrr Job Scraper
Mengambil data lowongan pekerjaan dari portal Kalibrr Indonesia dengan ekstraksi Next.js Data.
Mendukung deteksi langsung flag 'isOpenToFreshGrads', salary range, dan detail kualifikasi.
"""

import json
import re
import time
import urllib.parse
from typing import List, Dict, Any

from .base_scraper import BaseScraper, JobItem
from filters import (
    is_biology_relevant,
    match_location,
    is_freshgraduate_friendly,
    get_matched_biology_keywords,
    classify_biology_field,
    is_jabek_location
)
from config import REQUEST_DELAY

class KalibrrScraper(BaseScraper):
    """Scraper untuk platform Kalibrr Indonesia."""

    def __init__(self):
        super().__init__("Kalibrr")
        self.base_url = "https://www.kalibrr.com"

    def _format_salary(self, job_data: Dict[str, Any]) -> str:
        """Memformat rentang gaji jika ditampilkan oleh perusahaan."""
        if not job_data.get("salaryShown"):
            return "Kompetitif / Dirahasiakan"
        min_sal = job_data.get("baseSalary")
        max_sal = job_data.get("maximumSalary")
        curr = job_data.get("salaryCurrency", "IDR")
        interval = job_data.get("salaryInterval", "Bulan")

        if min_sal and max_sal:
            return f"{curr} {min_sal:,.0f} - {max_sal:,.0f} / {interval}"
        elif min_sal:
            return f"{curr} > {min_sal:,.0f} / {interval}"
        return "Kompetitif / Dirahasiakan"

    def _extract_location_str(self, job_data: Dict[str, Any]) -> str:
        """Mengekstrak nama kota dari data lokasi Kalibrr."""
        loc_data = job_data.get("googleLocation", {})
        if isinstance(loc_data, dict):
            addr = loc_data.get("addressComponents", {})
            city = addr.get("city") or addr.get("administrativeAreaLevel2") or addr.get("administrativeAreaLevel1")
            if city:
                return city

        locs = job_data.get("locations", [])
        if locs and isinstance(locs, list):
            for loc in locs:
                if isinstance(loc, dict) and loc.get("city"):
                    return loc.get("city")
        return "Indonesia"

    def scrape(
        self,
        keywords: List[str],
        locations: List[str] = None,
        max_results: int = 30
    ) -> List[JobItem]:
        """
        Scraping Kalibrr Indonesia untuk posisi biologi dan lab fresh graduate.
        """
        results: List[JobItem] = []
        seen_ids = set()

        search_terms = [
            "biologi", "microbiology", "laboratorium", "biotech",
            "quality-control", "chemist", "analis-lab", "food-safety",
            "haccp", "bioremediasi", "wwtp"
        ]

        for term in search_terms:
            if len(results) >= max_results:
                break

            target_url = f"{self.base_url}/job-board/co/Indonesia/te/{term}"
            try:
                resp = self.session.get(target_url, timeout=12)
                if resp.status_code != 200:
                    continue

                # Cari script __NEXT_DATA__
                match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
                if not match:
                    continue

                data = json.loads(match.group(1))
                page_props = data.get("props", {}).get("pageProps", {})
                jobs_list = page_props.get("jobs", [])

                for j in jobs_list:
                    if len(results) >= max_results:
                        break

                    job_id = str(j.get("id"))
                    if not job_id or job_id in seen_ids:
                        continue

                    title = j.get("name", "")
                    comp_info = j.get("company", {}) or {}
                    company = comp_info.get("name") or j.get("companyName") or "Perusahaan Terkemuka"
                    company_code = comp_info.get("code") or "company"
                    slug = j.get("slug", "")

                    raw_loc = self._extract_location_str(j)
                    raw_desc = j.get("description", "") or ""
                    raw_qual = j.get("qualifications", "") or ""
                    full_desc = f"{raw_desc}\n\nKualifikasi:\n{raw_qual}"

                    # Validasi lokasi (prioritaskan Jakarta & Bekasi / sekitarnya)
                    matched_loc, city_cat, display_loc = match_location(raw_loc)
                    if not is_jabek_location(raw_loc, include_surrounding=True):
                        # Jika lokasi tidak eksplisit di Jabek, cek apakah deskripsi menyebut Jakarta / Bekasi / Cikarang
                        desc_matched, desc_city_cat, desc_display_loc = match_location(full_desc)
                        if desc_matched and is_jabek_location(desc_display_loc, include_surrounding=True):
                            city_cat = desc_city_cat
                            display_loc = desc_display_loc
                        else:
                            continue

                    # Validasi relevansi biologi
                    if not is_biology_relevant(title, full_desc):
                        continue

                    # Validasi Fresh Graduate
                    is_fg_explicit = j.get("isOpenToFreshGrads")
                    is_fg = is_freshgraduate_friendly(
                        title=title,
                        description=full_desc,
                        experience_level_field=j.get("workExperience", ""),
                        is_explicit_freshgrad=is_fg_explicit
                    )
                    if not is_fg:
                        continue

                    seen_ids.add(job_id)

                    # Buat apply URL
                    apply_url = j.get("applyRedirectUrl")
                    if not apply_url:
                        apply_url = f"{self.base_url}/c/{company_code}/jobs/{job_id}/{slug}"

                    salary_str = self._format_salary(j)
                    matched_kws = get_matched_biology_keywords(title, full_desc)
                    field_category = classify_biology_field(title, full_desc)

                    clean_desc_text = re.sub(r'<[^>]+>', ' ', full_desc)
                    clean_desc_text = re.sub(r'\s+', ' ', clean_desc_text).strip()

                    job_item = JobItem(
                        id=f"kb-{job_id}",
                        title=title,
                        company=company,
                        location=display_loc if matched_loc else raw_loc,
                        city_category=city_cat,
                        is_fresh_graduate=True,
                        experience_level="Terbuka untuk Fresh Graduate" if is_fg_explicit else "Entry Level",
                        salary=salary_str,
                        description=clean_desc_text[:1200] + ("..." if len(clean_desc_text) > 1200 else ""),
                        field_category=field_category,
                        matched_keywords=matched_kws,
                        apply_url=apply_url,
                        posted_at=j.get("activationDate", "")[:10] if j.get("activationDate") else "Tersedia",
                        source="Kalibrr"
                    )
                    results.append(job_item)

                time.sleep(REQUEST_DELAY)

            except Exception:
                continue

        return results
