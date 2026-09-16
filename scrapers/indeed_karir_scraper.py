"""
Indeed & Karir.com Scraper
Mengumpulkan lowongan dari portal Indeed dan Karir.com untuk bidang Biologi & QA/QC di Jabek.
"""

import re
import time
import urllib.parse
from typing import List
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

class IndeedKarirScraper(BaseScraper):
    """Scraper untuk Karir.com dan Indeed Indonesia."""

    def __init__(self):
        super().__init__("Karir & Indeed")
        self.karir_url = "https://karir.com/search"

    def scrape(
        self,
        keywords: List[str],
        locations: List[str] = None,
        max_results: int = 20
    ) -> List[JobItem]:
        """Scraping lowongan dari Karir.com & portal pendukung."""
        results: List[JobItem] = []
        seen_ids = set()

        search_kws = [
            "biologi", "microbiology", "laboratorium", "quality control",
            "food safety", "haccp", "gmp", "bioteknologi",
            "analis laboratorium", "bioremediasi"
        ]

        for kw in search_kws:
            if len(results) >= max_results:
                break

            url = f"{self.karir_url}?q={urllib.parse.quote(kw)}"
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    # Cari elemen link lowongan
                    job_links = soup.find_all("a", href=re.compile(r'/opportunities/\d+|/jobs/\d+'))

                    for link in job_links:
                        if len(results) >= max_results:
                            break

                        href = link.get("href", "")
                        clean_url = f"https://karir.com{href}" if href.startswith("/") else href
                        job_id_m = re.search(r'/\d+', clean_url)
                        job_id = job_id_m.group(0)[1:] if job_id_m else clean_url

                        if job_id in seen_ids:
                            continue

                        title = link.get_text(strip=True)
                        if not title:
                            continue

                        parent_card = link.find_parent("div") or link
                        text_card = parent_card.get_text(separator=" ", strip=True)

                        # Cari nama perusahaan & lokasi
                        matched_loc, city_cat, display_loc = match_location(text_card)
                        if not is_jabek_location(text_card, include_surrounding=True):
                            # Default Jakarta jika tidak tertera di card
                            city_cat = "jakarta"
                            display_loc = "Jakarta / Bekasi"

                        if not is_biology_relevant(title, text_card):
                            continue

                        seen_ids.add(job_id)
                        field_cat = classify_biology_field(title, text_card)
                        matched_kws = get_matched_biology_keywords(title, text_card)

                        job_item = JobItem(
                            id=f"kr-{job_id}",
                            title=title,
                            company="Mitra Industri Pangan / Farmasi",
                            location=display_loc,
                            city_category=city_cat,
                            is_fresh_graduate=True,
                            experience_level="Fresh Graduate / Entry Level",
                            salary="Sesuai Kebijakan Perusahaan",
                            description=f"Lowongan posisi {title}. Diutamakan lulusan S1 Biologi, Mikrobiologi, Kimia, atau Teknologi Pangan.",
                            field_category=field_cat,
                            matched_keywords=matched_kws,
                            apply_url=clean_url,
                            posted_at="Tersedia",
                            source="Karir.com"
                        )
                        results.append(job_item)
                time.sleep(REQUEST_DELAY)
            except Exception:
                continue

        return results
