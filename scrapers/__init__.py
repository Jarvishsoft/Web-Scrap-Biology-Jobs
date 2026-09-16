"""
Package scrapers untuk mengumpulkan lowongan kerja dari berbagai portal:
- LinkedIn
- Glints
- JobStreet
- Kalibrr
- Indeed / Karir.com
"""

from .base_scraper import BaseScraper, JobItem
from .linkedin_scraper import LinkedInScraper
from .glints_scraper import GlintsScraper
from .jobstreet_scraper import JobStreetScraper
from .kalibrr_scraper import KalibrrScraper
from .indeed_karir_scraper import IndeedKarirScraper

__all__ = [
    "BaseScraper",
    "JobItem",
    "LinkedInScraper",
    "GlintsScraper",
    "JobStreetScraper",
    "KalibrrScraper",
    "IndeedKarirScraper"
]
