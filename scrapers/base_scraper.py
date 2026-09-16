"""
Base Scraper
Struktur dasar dan skema data untuk semua scraper lowongan pekerjaan.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import DEFAULT_HEADERS

@dataclass
class JobItem:
    """Skema data standar lowongan kerja."""
    id: str
    title: str
    company: str
    location: str
    city_category: str
    is_fresh_graduate: bool
    experience_level: str
    salary: str
    description: str
    field_category: str = "Biologi Umum"
    matched_keywords: List[str] = field(default_factory=list)
    apply_url: str = ""
    posted_at: str = ""
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BaseScraper(ABC):
    """Kelas dasar untuk modul web scraper."""

    def __init__(self, name: str):
        self.name = name
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Membuat HTTP session dengan retry otomatis dan headers standar."""
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)
        retry_strategy = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    @abstractmethod
    def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        max_results: int = 30
    ) -> List[JobItem]:
        """Metode utama scraping data pekerjaan."""
        pass
