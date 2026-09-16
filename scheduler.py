"""
Scheduler & Cron Job: Auto-Refresh Scraper Lowongan S1 Biologi
Menjalankan proses scraping, pemfilteran, dan pembaruan data secara otomatis setiap 5 menit.
"""

import argparse
import sys
import time
import datetime
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel

from config import BIOLOGY_KEYWORDS, OUTPUT_DIR
from main import run_scrapers, deduplicate_jobs
from exporters import export_to_excel, export_to_csv, export_to_json, export_to_dashboard

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()

def run_scraping_cycle(sources: List[str], max_results: int, cycle_num: int):
    """Menjalankan satu siklus scraping dan ekspor berkas."""
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    console.print(f"\n[bold cyan]╔═══════════════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print(f"[bold cyan]║[/bold cyan] [bold green]🔄 CRON SIKLUS #{cycle_num} | WAKTU: {now_str} WIB[/bold green] [bold cyan]║[/bold cyan]")
    console.print(f"[bold cyan]╚═══════════════════════════════════════════════════════════════════════╝[/bold cyan]")
    console.print(f"[dim]Memulai refresh otomatis lowongan QA/QC, Mikrobiologi, & WWTP di Jabek...[/dim]\n")

    # Jalankan Scrapers
    new_jobs = run_scrapers(sources, max_results=max_results)
    console.print(f"[bold green]✓ Berhasil menjaring {len(new_jobs)} lowongan bersih sesi ini.[/bold green]")

    # Inkremental append ke master data
    from storage import load_stored_jobs, merge_and_append_jobs, save_all_job_data, MASTER_JSON_PATH
    existing_jobs = load_stored_jobs(MASTER_JSON_PATH)
    combined_jobs, new_count = merge_and_append_jobs(existing_jobs, new_jobs)

    # Simpan ke semua format
    saved = save_all_job_data(combined_jobs)

    finish_time = datetime.datetime.now().strftime("%H:%M:%S")
    console.print(f"[bold green]✓ Seluruh file output berhasil disegarkan pada {finish_time} WIB[/bold green]")
    console.print(f"  • Status data: +{new_count} baru | Total: {len(combined_jobs)} lowongan ({len(existing_jobs)} lama tersimpan)")
    console.print(f"  • Excel     : [cyan]{saved['excel'].name}[/cyan]")
    console.print(f"  • Dashboard : [cyan]{saved['html'].name}[/cyan]")
    console.print(f"  • Data CSV  : [cyan]{saved['csv'].name}[/cyan]")

import threading
import webbrowser
import json as _json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# ─── State scraping real-time ────────────────────────────────────────────────
is_scraping_now = False
global_sources = ["linkedin", "glints", "jobstreet", "kalibrr", "karir"]
global_max_results = 10

scrape_status = {
    "running": False,
    "phase": "idle",          # idle | scraping | exporting | done | error
    "current_source": "",     # nama portal yang sedang discrape
    "sources_done": [],       # portal yang sudah selesai
    "sources_total": [],      # semua portal yang akan discrape
    "jobs_found": 0,
    "message": "Idle – menunggu perintah",
    "error": None,
    "finished_at": None,
}

def _update_status(**kwargs):
    """Update global scrape_status dict secara thread-safe."""
    scrape_status.update(kwargs)

# ─── Source label mapping ────────────────────────────────────────────────────
SOURCE_LABELS = {
    "linkedin":   "LinkedIn",
    "glints":     "Glints",
    "jobstreet":  "JobStreet",
    "kalibrr":    "Kalibrr",
    "karir":      "Indeed / Karir.com",
}

def trigger_manual_scrape():
    """Scraping on-demand dipicu dari tombol dashboard. Melaporkan progress per sumber."""
    global is_scraping_now
    if is_scraping_now:
        return
    is_scraping_now = True

    sources = list(global_sources)
    _update_status(
        running=True,
        phase="scraping",
        current_source="",
        sources_done=[],
        sources_total=sources,
        jobs_found=0,
        message="Memulai proses scraping...",
        error=None,
        finished_at=None,
    )

    try:
        console.print("[bold yellow]⚡ Permintaan Refresh & Scrape Diterima dari Web Dashboard...[/bold yellow]")

        # ── Import scraper classes langsung agar bisa iterasi per-sumber ──
        from scrapers import (
            LinkedInScraper, GlintsScraper, JobStreetScraper,
            KalibrrScraper, IndeedKarirScraper
        )
        from scrapers.base_scraper import JobItem
        from filters.location_matcher import is_jabek_location
        from filters.freshgrad_matcher import categorize_field

        scrapers_map = {
            "linkedin":   LinkedInScraper(),
            "glints":     GlintsScraper(),
            "jobstreet":  JobStreetScraper(),
            "kalibrr":    KalibrrScraper(),
            "karir":      IndeedKarirScraper(),
        }

        from config import BIOLOGY_KEYWORDS
        all_jobs: list = []
        done_sources: list = []

        for src in sources:
            scraper = scrapers_map.get(src)
            if not scraper:
                done_sources.append(src)
                continue

            label = SOURCE_LABELS.get(src, src.upper())
            _update_status(
                phase="scraping",
                current_source=src,
                sources_done=list(done_sources),
                message=f"Scraping {label}... ({len(done_sources)+1}/{len(sources)})",
            )
            console.print(f"  [cyan]→ Scraping {label}...[/cyan]")

            try:
                jobs = scraper.scrape(keywords=BIOLOGY_KEYWORDS[:10], max_results=global_max_results)
                all_jobs.extend(jobs)
                _update_status(jobs_found=len(all_jobs))
                console.print(f"  [green]✓[/green] {label}: {len(jobs)} lowongan")
            except Exception as e:
                console.print(f"  [red]✗[/red] {label}: {e}")

            done_sources.append(src)
            _update_status(sources_done=list(done_sources))

        # ── Deduplicate ──
        seen = set()
        unique_jobs = []
        for j in all_jobs:
            key = f"{j.title.lower().strip()}_{j.company.lower().strip()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(j)

        # ── Inkremental Append: Gabungkan dengan data lama yang tersimpan ──
        from storage import load_stored_jobs, merge_and_append_jobs, save_all_job_data, MASTER_JSON_PATH
        existing_jobs = load_stored_jobs(MASTER_JSON_PATH)
        combined_jobs, new_count = merge_and_append_jobs(existing_jobs, unique_jobs)

        _update_status(
            phase="exporting",
            current_source="",
            jobs_found=len(combined_jobs),
            message=f"+{new_count} baru ditambahkan. Total {len(combined_jobs)} lowongan tersimpan. Menyimpan...",
        )
        console.print(f"[bold green]✓ Selesai: +{new_count} lowongan baru ditambahkan. Total: {len(combined_jobs)} lowongan (data lama tersimpan).[/bold green]")

        # ── Export Seluruh Data Gabungan ──
        save_all_job_data(combined_jobs)

        finish_time = datetime.datetime.now().strftime("%H:%M:%S")
        _update_status(
            running=False,
            phase="done",
            jobs_found=len(combined_jobs),
            message=f"✅ Selesai! +{new_count} baru ditambahkan (total {len(combined_jobs)} lowongan) pada {finish_time} WIB.",
            finished_at=finish_time,
        )
        console.print(f"[bold green]✓ Dashboard & semua file diperbarui pada {finish_time} WIB[/bold green]")

    except Exception as e:
        _update_status(
            running=False,
            phase="error",
            message=f"❌ Scraping gagal: {e}",
            error=str(e),
        )
        console.print(f"[bold red]✗ Scraping error: {e}[/bold red]")
    finally:
        is_scraping_now = False


class DashboardHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUTPUT_DIR), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/status"):
            body = _json.dumps(scrape_status, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/scrape"):
            if is_scraping_now:
                body = _json.dumps({"status": "already_running", "message": scrape_status["message"]}).encode()
            else:
                threading.Thread(target=trigger_manual_scrape, daemon=True).start()
                body = _json.dumps({"status": "scraping_started"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        pass

def start_http_server(port=8000):
    for p in (port, 8080, 8888):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", p), DashboardHTTPHandler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            return p
        except Exception:
            continue
    return None


def main():
    global global_sources, global_max_results
    parser = argparse.ArgumentParser(description="Cron Job Auto-Scraper Lowongan S1 Biologi Jabek")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Interval refresh otomatis dalam menit (default: 5 menit)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maksimal lowongan per sumber dalam tiap siklus (default: 10)"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["linkedin", "glints", "jobstreet", "kalibrr", "karir"],
        help="Sumber portal yang discrape"
    )
    parser.add_argument(
        "--open-dashboard",
        action="store_true",
        help="Otomatis membuka web dashboard di browser"
    )

    args = parser.parse_args()
    global_sources = args.sources
    global_max_results = args.max_results
    interval_seconds = args.interval * 60

    # Jalankan server dashboard lokal
    server_port = start_http_server(8000)
    server_url = f"http://localhost:{server_port}/dashboard.html" if server_port else "File lokal output/dashboard.html"

    console.print(Panel(
        f"""[bold green]CRON JOB AUTO-REFRESH & LIVE DASHBOARD SERVER AKTIF[/bold green]
• Interval Otomatis     : [bold yellow]{args.interval} Menit[/bold yellow] ({interval_seconds} detik)
• Portal Sumber         : [cyan]{', '.join(s.upper() for s in args.sources)}[/cyan]
• Target Lowongan       : [white]S1 Biologi (QA/QC, Mikrobiologi, WWTP) - Jakarta & Bekasi[/white]
• Server Web Dashboard  : [bold underline cyan]{server_url}[/bold underline cyan]
• Tombol 'Refresh Data' : [green]Siap Menerima Trigger On-Demand dari Browser[/green]

[dim]Tekan Ctrl + C di jendela ini untuk menghentikan auto-scraper kapan saja.[/dim]""",
        title="[bold cyan]Auto-Scraper & Live Server[/bold cyan]",
        border_style="cyan"
    ))

    if args.open_dashboard:
        url_to_open = server_url if server_port else f"file://{(OUTPUT_DIR / 'dashboard.html').resolve()}"
        webbrowser.open(url_to_open)

    cycle_count = 1
    try:
        while True:
            run_scraping_cycle(args.sources, args.max_results, cycle_count)
            cycle_count += 1

            next_run = datetime.datetime.now() + datetime.timedelta(seconds=interval_seconds)
            console.print(f"\n[dim]⏳ Menunggu {args.interval} menit untuk siklus berikutnya... (Jadwal: {next_run.strftime('%H:%M:%S')} WIB)[/dim]")
            
            # Hitung mundur
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cron Job dihentikan oleh pengguna. Sampai jumpa![/bold yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main()
