"""
LinkedIn Guest Job Scraper
Mengambil data lowongan pekerjaan publik dari LinkedIn Guest API tanpa perlu akun/login.
Target: Jakarta & Bekasi (Cikarang) untuk Fresh Graduate Biologi.
"""

import time
import re
import urllib.parse
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

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

class LinkedInScraper(BaseScraper):
    """Scraper untuk LinkedIn Jobs publik."""

    def __init__(self):
        super().__init__("LinkedIn")
        self.search_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        self.detail_url_base = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting"

    def _fetch_job_detail(self, job_id: str) -> Dict[str, Any]:
        """Mengambil rincian kualifikasi dan deskripsi pekerjaan."""
        url = f"{self.detail_url_base}/{job_id}"
        detail_data = {
            "description": "",
            "seniority": "",
            "employment_type": "",
            "industry": ""
        }
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Deskripsi pekerjaan
                desc_div = soup.find("div", class_=re.compile(r"show-more-less-html__markup"))
                if desc_div:
                    detail_data["description"] = desc_div.get_text(separator="\n", strip=True)
                
                # Kriteria pekerjaan (Seniority, Tipe, Industri)
                headers = [h.get_text(strip=True) for h in soup.find_all("h3", class_="description__job-criteria-subheader")]
                values = [v.get_text(strip=True) for v in soup.find_all("span", class_=re.compile(r"description__job-criteria-text"))]
                criteria_map = dict(zip(headers, values))
                
                detail_data["seniority"] = criteria_map.get("Tingkat senioritas", criteria_map.get("Seniority level", ""))
                detail_data["employment_type"] = criteria_map.get("Jenis pekerjaan", criteria_map.get("Employment type", ""))
                detail_data["industry"] = criteria_map.get("Industri", criteria_map.get("Industries", ""))
        except Exception:
            pass  # Fallback gracefully jika gagal load detail spesifik
        return detail_data

    def scrape(
        self,
        keywords: List[str],
        locations: List[str] = None,
        max_results: int = 30
    ) -> List[JobItem]:
        """
        Menjalankan pencarian lowongan LinkedIn berdasarkan kata kunci dan lokasi target.
        """
        if not locations:
            locations = [
                "Jakarta, Indonesia",
                "Bekasi, Jawa Barat, Indonesia",
                "Cikarang, Jawa Barat, Indonesia"
            ]

        results: List[JobItem] = []
        seen_ids = set()

        for location in locations:
            for kw in keywords:
                if len(results) >= max_results:
                    break

                start = 0
                params = {
                    "keywords": kw,
                    "location": location,
                    "f_E": "2",  # Filter LinkedIn: Entry Level / Fresh Graduate
                    "start": start
                }

                try:
                    resp = self.session.get(self.search_url, params=params, timeout=12)
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")
                    job_cards = soup.find_all("div", class_="base-card")

                    for card in job_cards:
                        if len(results) >= max_results:
                            break

                        # Ekstraksi Job ID & Link
                        link_tag = card.find("a", class_=re.compile(r"base-card__full-link"))
                        if not link_tag or not link_tag.get("href"):
                            continue

                        raw_href = link_tag.get("href", "")
                        clean_url = raw_href.split("?")[0]
                        job_id_match = re.search(r'-(\d+)$', clean_url)
                        job_id = job_id_match.group(1) if job_id_match else clean_url

                        if job_id in seen_ids:
                            continue
                        seen_ids.add(job_id)

                        # Judul posisi
                        title_tag = card.find("h3", class_="base-search-card__title")
                        title = title_tag.get_text(strip=True) if title_tag else ""

                        # Nama Perusahaan
                        company_tag = card.find("h4", class_="base-search-card__subtitle")
                        company = company_tag.get_text(strip=True) if company_tag else "Perusahaan Tidak Disebutkan"

                        # Lokasi
                        loc_tag = card.find("span", class_="job-search-card__location")
                        raw_loc = loc_tag.get_text(strip=True) if loc_tag else location

                        # Tanggal posting
                        date_tag = card.find("time", class_=re.compile(r"job-search-card__listdate"))
                        posted_at = date_tag.get_text(strip=True) if date_tag else ""

                        # Validasi awal relevansi biologi dan lokasi
                        matched_loc, city_cat, display_loc = match_location(raw_loc)
                        if not is_jabek_location(raw_loc, include_surrounding=True):
                            continue

                        # Ambil rincian pekerjaan (deskripsi, syarat, level)
                        time.sleep(0.3)
                        detail = self._fetch_job_detail(job_id)
                        description = detail.get("description", "")
                        seniority = detail.get("seniority", "Entry level")

                        # Cek relevansi biologi
                        if not is_biology_relevant(title, description):
                            continue

                        # Cek kecocokan fresh graduate
                        is_fg = is_freshgraduate_friendly(
                            title=title,
                            description=description,
                            experience_level_field=seniority
                        )
                        if not is_fg:
                            continue

                        matched_kws = get_matched_biology_keywords(title, description)
                        field_category = classify_biology_field(title, description)

                        job_item = JobItem(
                            id=f"li-{job_id}",
                            title=title,
                            company=company,
                            location=display_loc if matched_loc else raw_loc,
                            city_category=city_cat,
                            is_fresh_graduate=True,
                            experience_level=seniority or "Entry Level (Fresh Graduate)",
                            salary="Sesuai Kebijakan Perusahaan",
                            description=description[:1200] + ("..." if len(description) > 1200 else ""),
                            field_category=field_category,
                            matched_keywords=matched_kws,
                            apply_url=clean_url,
                            posted_at=posted_at,
                            source="LinkedIn"
                        )
                        results.append(job_item)

                    time.sleep(REQUEST_DELAY)

                except Exception as e:
                    # Lanjut ke kata kunci berikutnya jika terjadi kendala jaringan
                    continue

        return results
