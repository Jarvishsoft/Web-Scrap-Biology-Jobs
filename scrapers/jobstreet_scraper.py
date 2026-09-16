"""
JobStreet Indonesia Scraper
Mengambil data lowongan pekerjaan dari portal JobStreet Indonesia untuk kawasan Jakarta & Bekasi/Cikarang.
Fokus pada posisi QA/QC, Food Safety, HACCP/GMP, Mikrobiologi, WWTP, dan Analis Lab.
"""

import re
import time
import urllib.parse
from typing import List, Dict, Any
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

class JobStreetScraper(BaseScraper):
    """Scraper untuk platform JobStreet Indonesia."""

    def __init__(self):
        super().__init__("JobStreet")
        self.base_url = "https://id.jobstreet.com"
        # Tambahkan header khusus agar tidak diblokir Jobstreet
        self.session.headers.update({
            "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        })

    def scrape(
        self,
        keywords: List[str],
        locations: List[str] = None,
        max_results: int = 30
    ) -> List[JobItem]:
        """
        Scraping JobStreet Indonesia untuk posisi biologi, QA/QC, mikrobiologi, & WWTP.
        """
        results: List[JobItem] = []
        seen_ids = set()

        # Format keyword untuk URL Jobstreet (huruf kecil tanpa spasi -> tanda minus)
        target_queries = [
            "biologi", "microbiology", "quality-control",
            "food-safety", "haccp", "laboratorium", "wwtp"
        ]

        target_locations = [
            ("in-Jakarta", "Jakarta"),
            ("in-Bekasi-Jawa-Barat", "Bekasi"),
            ("in-Cikarang-Jawa-Barat", "Cikarang")
        ]

        for query in target_queries:
            for loc_slug, loc_name in target_locations:
                if len(results) >= max_results:
                    break

                url = f"{self.base_url}/id/job-search/{query}-jobs/{loc_slug}/"

                try:
                    resp = self.session.get(url, timeout=12)
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")
                    articles = soup.find_all("article")

                    for art in articles:
                        if len(results) >= max_results:
                            break

                        # Ambil link pekerjaan
                        job_link = art.find("a", href=re.compile(r'/id/job/\d+'))
                        if not job_link:
                            continue

                        raw_href = job_link.get("href", "")
                        clean_href = raw_href.split("?")[0]
                        job_id_m = re.search(r'/job/(\d+)', clean_href)
                        job_id = job_id_m.group(1) if job_id_m else clean_href

                        if job_id in seen_ids:
                            continue

                        # Judul posisi
                        title = job_link.get_text(strip=True)
                        if not title:
                            # Coba cari link lain dengan teks
                            for l in art.find_all("a", href=re.compile(r'/id/job/\d+')):
                                if l.get_text(strip=True):
                                    title = l.get_text(strip=True)
                                    break

                        if not title:
                            continue

                        # Nama Perusahaan
                        comp_tag = art.find("a", href=re.compile(r'/id/companies/|-jobs'))
                        company = comp_tag.get_text(strip=True) if comp_tag else "Perusahaan Mitra JobStreet"

                        # Lokasi
                        loc_tag = art.find("a", href=re.compile(r'/in-'))
                        raw_loc = loc_tag.get_text(strip=True) if loc_tag else loc_name

                        # Cuplikan deskripsi / teaser
                        teaser_tag = art.find("span", attrs={"data-automation": "jobTeaser"})
                        teaser_text = teaser_tag.get_text(strip=True) if teaser_tag else ""
                        full_text = f"{title} {company} {teaser_text}"

                        # Validasi lokasi
                        matched_loc, city_cat, display_loc = match_location(raw_loc)
                        if not is_jabek_location(raw_loc, include_surrounding=True):
                            continue

                        # Validasi relevansi biologi
                        if not is_biology_relevant(title, full_text):
                            continue

                        # Validasi fresh graduate
                        if not is_freshgraduate_friendly(title=title, description=full_text):
                            continue

                        seen_ids.add(job_id)

                        # Estimasi gaji
                        sal_tag = art.find("span", attrs={"data-automation": "jobSalary"})
                        salary_str = sal_tag.get_text(strip=True) if sal_tag else "Sesuai Kebijakan Perusahaan"

                        field_category = classify_biology_field(title, full_text)
                        matched_kws = get_matched_biology_keywords(title, full_text)
                        full_apply_url = f"{self.base_url}{clean_href}" if clean_href.startswith("/") else clean_href

                        job_item = JobItem(
                            id=f"js-{job_id}",
                            title=title,
                            company=company,
                            location=display_loc if matched_loc else raw_loc,
                            city_category=city_cat,
                            is_fresh_graduate=True,
                            experience_level="Fresh Graduate / Entry Level",
                            salary=salary_str,
                            description=teaser_text or f"Posisi {title} di {company}. Terbuka untuk lulusan biologi / kimia / farmasi / pangan.",
                            field_category=field_category,
                            matched_keywords=matched_kws,
                            apply_url=full_apply_url,
                            posted_at="Tersedia",
                            source="JobStreet"
                        )
                        results.append(job_item)

                    time.sleep(REQUEST_DELAY)

                except Exception:
                    continue

        return results
