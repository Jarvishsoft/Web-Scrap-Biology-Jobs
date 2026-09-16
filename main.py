"""
Main Entrypoint: Web Scraper Lowongan Kerja S1 Biologi Fresh Graduate (Jabek)
Khusus Peminatan: QA/QC & Food Safety, HACCP & GMP, Mikrobiologi, Mikologi, Bioremediasi & WWTP
Portal Sumber: LinkedIn, Glints, JobStreet, Kalibrr, Indeed/Karir.com
"""

import argparse
import sys
import webbrowser
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from config import BIOLOGY_KEYWORDS, OUTPUT_DIR
from scrapers import (
    BaseScraper,
    JobItem,
    LinkedInScraper,
    GlintsScraper,
    JobStreetScraper,
    KalibrrScraper,
    IndeedKarirScraper
)
from exporters import export_to_excel, export_to_csv, export_to_json, export_to_dashboard

# Pastikan output konsol Windows mendukung karakter UTF-8
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()

def print_welcome_banner():
    """Menampilkan banner selamat datang khusus S1 Biologi UNSOED & Fresh Graduate."""
    banner = """========================================================================
  WEB SCRAPER LOWONGAN KERJA S1 BIOLOGI (FRESH GRADUATE)
  Fokus Bidang: QA/QC, Food Safety (HACCP/GMP), Mikrobiologi & WWTP
  Area Target : Jakarta & Bekasi (Jabek / Cikarang Industrial Estate)
  Sumber Portal: LinkedIn, Glints, JobStreet, Kalibrr & Karir.com
========================================================================"""
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[dim]Keahlian Terpantau: QA/QC Pangan/Farmasi, HACCP, GMP, Mikrobiologi, Mikologi, Bioremediasi & IPAL[/dim]\n")

def deduplicate_jobs(jobs: List[JobItem]) -> List[JobItem]:
    """Menghapus duplikasi lowongan berdasarkan judul & nama perusahaan."""
    unique_jobs = []
    seen = set()
    for j in jobs:
        key = f"{j.title.lower().strip()}_{j.company.lower().strip()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
    return unique_jobs

def run_scrapers(selected_sources: List[str], max_results: int) -> List[JobItem]:
    """Menjalankan scraper terpilih dari berbagai portal karir."""
    scrapers_map = {
        "linkedin": LinkedInScraper(),
        "glints": GlintsScraper(),
        "jobstreet": JobStreetScraper(),
        "kalibrr": KalibrrScraper(),
        "karir": IndeedKarirScraper()
    }

    all_jobs: List[JobItem] = []

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:

        for src_name in selected_sources:
            scraper: BaseScraper = scrapers_map.get(src_name)
            if not scraper:
                continue

            task = progress.add_task(f"[cyan]Scraping {scraper.name}...[/cyan]", total=100)
            progress.update(task, advance=15)

            try:
                jobs = scraper.scrape(
                    keywords=BIOLOGY_KEYWORDS[:10],
                    max_results=max_results
                )
                progress.update(task, advance=85)
                all_jobs.extend(jobs)
                console.print(f"  [green]✓[/green] {scraper.name}: Menemukan [bold]{len(jobs)}[/bold] lowongan relevan.")
            except Exception as e:
                console.print(f"  [red]✗[/red] Gagal scraping {scraper.name}: {e}")
                progress.update(task, completed=100)

    return deduplicate_jobs(all_jobs)

def display_results_table(jobs: List[JobItem]):
    """Menampilkan tabel hasil scraping ke terminal console."""
    if not jobs:
        console.print("[yellow]Tidak ada lowongan yang ditemukan untuk kriteria saat ini.[/yellow]")
        return

    table = Table(title="[bold green]Lowongan S1 Biologi Fresh Graduate Terjaring (Jabek)[/bold green]", border_style="cyan")
    table.add_column("No", justify="center", style="dim", width=4)
    table.add_column("Posisi / Judul Lowongan", style="bold white", min_width=24)
    table.add_column("Perusahaan", style="cyan", min_width=18)
    table.add_column("Area", justify="center", style="magenta", width=12)
    table.add_column("Fokus Bidang Keahlian", style="bold green", min_width=22)
    table.add_column("Sumber", justify="center", style="blue", width=10)
    table.add_column("Skill Terdeteksi", style="dim", min_width=18)

    for i, job in enumerate(jobs[:25], 1):
        area_label = "Bekasi/Ckrg" if job.city_category == "bekasi" else "Jakarta"
        keywords_str = ", ".join(job.matched_keywords[:3]) if job.matched_keywords else "-"
        table.add_row(
            str(i),
            job.title[:32],
            job.company[:22],
            area_label,
            job.field_category[:25],
            job.source,
            keywords_str
        )

    console.print(table)
    if len(jobs) > 25:
        console.print(f"[dim]* Menampilkan 25 dari total {len(jobs)} lowongan. Buka file Excel atau Web Dashboard untuk melihat seluruh data.[/dim]\n")

def main():
    parser = argparse.ArgumentParser(description="Web Scraper Lowongan S1 Biologi Fresh Graduate (Jabek)")
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["linkedin", "glints", "jobstreet", "kalibrr", "karir"],
        choices=["linkedin", "glints", "jobstreet", "kalibrr", "karir", "all"],
        help="Portal sumber scraper (default: linkedin glints jobstreet kalibrr karir)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=25,
        help="Maksimal lowongan per sumber (default: 25)"
    )
    parser.add_argument(
        "--open-dashboard",
        action="store_true",
        help="Otomatis membuka web dashboard di browser setelah scraping selesai"
    )

    args = parser.parse_args()
    print_welcome_banner()

    sources = ["linkedin", "glints", "jobstreet", "kalibrr", "karir"] if "all" in args.sources else args.sources
    console.print(f"[bold]Target Sumber:[/bold] {', '.join(s.upper() for s in sources)}")
    console.print(f"[bold]Maksimal Lowongan:[/bold] {args.max_results} per portal\n")

    # Jalankan Scraping
    new_jobs = run_scrapers(sources, max_results=args.max_results)
    console.print(f"\n[bold green]Lowongan Bersih Terjaring Sesi Ini:[/bold green] [bold white]{len(new_jobs)}[/bold white]")

    # Muat data lama & gabungkan secara inkremental (jangan hapus data lama)
    from storage import load_stored_jobs, merge_and_append_jobs, save_all_job_data, MASTER_JSON_PATH
    existing_jobs = load_stored_jobs(MASTER_JSON_PATH)
    all_jobs, new_count = merge_and_append_jobs(existing_jobs, new_jobs)

    console.print(f"[bold cyan]🔄 Penggabungan Data (Append Incremental):[/bold cyan]")
    console.print(f"  • Data lama tersimpan : [bold]{len(existing_jobs)}[/bold] lowongan (tetap aman)")
    console.print(f"  • Lowongan baru unik  : [bold green]+{new_count}[/bold green] lowongan ditambahkan")
    console.print(f"  • Total katalog aktif : [bold yellow]{len(all_jobs)}[/bold yellow] lowongan\n")

    # Tampilkan Ringkasan Tabel
    display_results_table(all_jobs)

    # Ekspor ke berbagai format dengan nama kolom ramah Indonesia
    saved = save_all_job_data(all_jobs)
    excel_saved = saved["excel"]
    csv_saved = saved["csv"]
    json_saved = saved["json"]
    html_saved = saved["html"]

    # Ringkasan Spesialisasi
    qa_count = sum(1 for j in all_jobs if "QA/QC" in j.field_category or "Food Safety" in j.field_category)
    micro_count = sum(1 for j in all_jobs if "Mikro" in j.field_category)
    wwtp_count = sum(1 for j in all_jobs if "WWTP" in j.field_category or "Waste" in j.field_category)
    jkt_count = sum(1 for j in all_jobs if j.city_category == "jakarta")
    bekasi_count = sum(1 for j in all_jobs if j.city_category == "bekasi")

    summary_text = f"""[bold]Ringkasan Kesesuaian Bidang Keahlian (Total {len(all_jobs)} Lowongan):[/bold]
• QA/QC & Food Safety (HACCP/GMP) : [bold green]{qa_count}[/bold green] lowongan
• Mikrobiologi & Mikologi         : [bold green]{micro_count}[/bold green] lowongan
• Bioremediasi & WWTP/IPAL         : [bold green]{wwtp_count}[/bold green] lowongan
• Penempatan Jakarta : [bold yellow]{jkt_count}[/bold yellow] | Bekasi/Cikarang : [bold yellow]{bekasi_count}[/bold yellow]

[bold]Penyimpanan Inkremental Aktif (Data Lama Tetap Tersimpan):[/bold]
1. [green]Excel (.xlsx)[/green]   : [cyan]{excel_saved.name}[/cyan] (Link lamaran aktif di setiap baris pekerjaan)
2. [green]Web Dashboard[/green]  : [cyan]{html_saved.name}[/cyan] (Filter spesialisasi & ekspor Excel browser)
3. [green]Data CSV[/green]       : [cyan]{csv_saved.name}[/cyan] (Header Indonesia, ramah dibuka)
4. [green]Data JSON[/green]      : [cyan]{json_saved.name}[/cyan] (Database master persisten)"""

    console.print(Panel(summary_text, title="[bold green]Scraping & Penambahan Data Selesai[/bold green]", border_style="green"))

    if args.open_dashboard:
        console.print("[cyan]Membuka Web Dashboard di browser...[/cyan]")
        webbrowser.open(f"file://{html_saved.resolve()}")

if __name__ == "__main__":
    main()
