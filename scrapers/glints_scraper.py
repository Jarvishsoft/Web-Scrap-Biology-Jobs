"""
Glints Job Scraper
Mengambil data lowongan pekerjaan langsung dari portal Glints Indonesia
dengan ekstraksi data Next.js SSR (Explore Jobs).
Mendukung filter QA/QC, Mikrobiologi, Food Safety, HACCP/GMP, dan WWTP di Jabek.
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

class GlintsScraper(BaseScraper):
    """Scraper untuk platform Glints Indonesia."""

    def __init__(self):
        super().__init__("Glints")
        self.explore_url = "https://glints.com/id/opportunities/jobs/explore"
        self.base_url = "https://glints.com/id/opportunities/jobs"

    def _format_salary(self, job_data: Dict[str, Any]) -> str:
        """Memformat rentang gaji Glints jika ada."""
        salaries = job_data.get("salaries") or []
        if isinstance(salaries, list) and len(salaries) > 0:
            sal = salaries[0]
            if isinstance(sal, dict):
                min_s = sal.get("minAmount")
                max_s = sal.get("maxAmount")
                curr = sal.get("currencyCode", "IDR")
                if min_s and max_s:
                    return f"{curr} {min_s:,.0f} - {max_s:,.0f}"
                elif min_s:
                    return f"{curr} > {min_s:,.0f}"
        return "Kompetitif / Dirahasiakan"

    def _extract_location(self, job_data: Dict[str, Any]) -> str:
        """Mengekstrak informasi lokasi kota dari Glints."""
        loc = job_data.get("location")
        if loc and isinstance(loc, str) and loc.strip():
            return loc.strip()

        city_obj = job_data.get("city")
        if isinstance(city_obj, dict) and city_obj.get("name"):
            city_name = city_obj.get("name")
            sub_div = job_data.get("citySubDivision")
            if isinstance(sub_div, dict) and sub_div.get("name"):
                return f"{sub_div.get('name')}, {city_name}"
            return city_name

        country_obj = job_data.get("country")
        if isinstance(country_obj, dict) and country_obj.get("name"):
            return country_obj.get("name")

        return "Indonesia"

    def scrape(
        self,
        keywords: List[str],
        locations: List[str] = None,
        max_results: int = 30
    ) -> List[JobItem]:
        """
        Menjalankan pencarian lowongan di Glints untuk keahlian biologi fresh graduate.
        """
        results: List[JobItem] = []
        seen_ids = set()

        search_keywords = keywords[:20] if keywords else [
            "biologi", "microbiology", "analis mikrobiologi", "bioteknologi",
            "qc microbiology", "qa food safety", "haccp", "gmp",
            "bioremediasi", "wwtp biologi", "analis laboratorium"
        ]

        for kw in search_keywords:
            if len(results) >= max_results:
                break

            params = {
                "keyword": kw,
                "country": "ID"
            }
            query_str = urllib.parse.urlencode(params)
            url = f"{self.explore_url}?{query_str}"

            try:
                resp = self.session.get(url, timeout=12)
                if resp.status_code != 200:
                    continue

                m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
                if not m:
                    continue

                data = json.loads(m.group(1))
                props = data.get("props", {}).get("pageProps", {})
                initial_jobs = props.get("initialJobs", {})
                jobs_list = initial_jobs.get("jobsInPage", []) if isinstance(initial_jobs, dict) else []

                for j in jobs_list:
                    if len(results) >= max_results:
                        break

                    job_id = j.get("id")
                    if not job_id or job_id in seen_ids:
                        continue

                    title = j.get("title", "")
                    comp_obj = j.get("company")
                    company = comp_obj.get("name", "Perusahaan") if isinstance(comp_obj, dict) else "Perusahaan"

                    raw_loc = self._extract_location(j)
                    min_exp = j.get("minYearsOfExperience")
                    max_exp = j.get("maxYearsOfExperience")

                    # Validasi Lokasi Jakarta / Bekasi / Jabodetabek
                    matched_loc, city_cat, display_loc = match_location(raw_loc)
                    if not is_jabek_location(raw_loc, include_surrounding=True):
                        continue

                    # Kualifikasi pengalaman (0 - 1 tahun disukai)
                    if min_exp is not None and min_exp > 2:
                        continue

                    # Ambil skills tags
                    skills_list = [s.get("name", "") for s in (j.get("skills") or []) if isinstance(s, dict)]
                    full_text = f"{title} {' '.join(skills_list)}"

                    # Validasi relevansi biologi/QA/QC/WWTP
                    if not is_biology_relevant(title, full_text):
                        continue

                    seen_ids.add(job_id)

                    exp_label = "Fresh Graduate / Entry Level"
                    if min_exp is not None and max_exp is not None:
                        exp_label = f"{min_exp} - {max_exp} Tahun Pengalaman"
                    elif min_exp == 0 or min_exp is None:
                        exp_label = "Terbuka untuk Fresh Graduate (0-1 Tahun)"

                    field_category = classify_biology_field(title, full_text)
                    matched_kws = get_matched_biology_keywords(title, full_text)
                    apply_url = f"{self.base_url}/{job_id}"
                    salary_str = self._format_salary(j)

                    job_item = JobItem(
                        id=f"gl-{job_id[:8]}",
                        title=title,
                        company=company,
                        location=display_loc if matched_loc else raw_loc,
                        city_category=city_cat,
                        is_fresh_graduate=True,
                        experience_level=exp_label,
                        salary=salary_str,
                        description=f"Keahlian Terkait: {', '.join(skills_list) if skills_list else 'Sains / Biologi / QA / QC'}",
                        field_category=field_category,
                        matched_keywords=matched_kws,
                        apply_url=apply_url,
                        posted_at=j.get("createdAt", "")[:10] if j.get("createdAt") else "Tersedia",
                        source="Glints"
                    )
                    results.append(job_item)

                time.sleep(REQUEST_DELAY)

            except Exception:
                continue

        return results
