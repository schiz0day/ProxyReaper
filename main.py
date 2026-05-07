#!/usr/bin/env python3
"""Professional Proxy Scraper for OpenBullet2."""
import argparse
import sys
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

from proxyscraper.scraper.aggregator import ProxyAggregator
from proxyscraper.validators.validator import ProxyValidator
from proxyscraper.exporters.exporter import ProxyExporter

console = Console()


def print_banner():
    """Print ASCII art banner."""
    banner = Text(r"""
  ____                      ____                            
 |  _ \ _ __ _____  ___   _|  _ \ ___  __ _ _ __   ___ _ __ s
 | |_) | '__/ _ \ \/ / | | | |_) / _ \/ _` | '_ \ / _ \ '__|
 |  __/| | | (_) >  <| |_| |  _ <  __/ (_| | |_) |  __/ |   
 |_|   |_|  \___/_/\_\\__, |_| \_\___|\__,_| .__/ \___|_|   
                      |___/                |_|             
""", style="bold cyan")
    console.print(banner)
    console.print(Panel(
        "[bold white]Professional Proxy Scraper v1.0.0[/bold white]\n"
        "[dim]Optimized for OpenBullet2 | High Quality Proxies[/dim]",
        border_style="blue",
    ))
    console.print()


def cmd_scrape(args):
    """Scrape proxies from multiple sources."""
    console.print(f"[yellow][*] Scraping proxies from {len(args.sources) if args.sources else 'all'} sources...[/yellow]\n")

    aggregator = ProxyAggregator(timeout=args.timeout)

    sources = args.sources if args.sources else None

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scraping proxies...", total=None)
        proxies = aggregator.get_all_proxies(scraper_names=sources)
        progress.update(task, completed=True)

    console.print(f"\n[green][+] Scraped {len(proxies)} unique proxies[/green]\n")

    if args.save:
        exporter = ProxyExporter(proxies)
        filepath = exporter.export(args.save, fmt=args.format)
        console.print(f"[green][+] Saved to {filepath}[/green]")

    if not args.no_check:
        cmd_check(proxies, args)

    return proxies


def cmd_check(proxies, args):
    """Check proxies for validity and speed."""
    console.print(f"\n[yellow][*] Validating {len(proxies)} proxies...[/yellow]")
    console.print(f"[dim]Threads: {args.threads} | Timeout: {args.check_timeout}s[/dim]\n")

    validator = ProxyValidator(
        timeout=args.check_timeout,
        max_threads=args.threads,
    )

    checked = 0
    valid = 0
    total = len(proxies)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Checking proxies...", total=total)

        def on_progress(c, t, v):
            nonlocal checked, valid
            checked = c
            valid = v
            progress.update(task, completed=checked, description=f"Checking: {checked}/{total} | Valid: {valid}")

        validator.progress_callback = on_progress

        valid_proxies = validator.validate_all(
            proxies,
            protocol_filter=args.protocol,
            min_speed=args.max_speed if args.max_speed else None,
            anonymity_level=args.anonymity,
            check_anon=args.check_anonymity,
        )

        progress.update(task, completed=total)

    console.print(f"\n[green][+] Valid: {len(valid_proxies)}/{total} proxies ({len(valid_proxies)*100//max(total,1)}% success rate)[/green]\n")

    if args.save_checked:
        filepath = args.save_checked
    elif args.save:
        filepath = args.save.replace(".txt", "_checked.txt")
    else:
        filepath = "proxies_checked.txt"

    exporter = ProxyExporter(valid_proxies)

    if args.ob_format:
        exporter.export_openbullet(filepath)
        console.print(f"[green][+] Saved OpenBullet format to {filepath}[/green]")
    else:
        exporter.export(filepath, fmt=args.format, protocol=args.protocol)
        console.print(f"[green][+] Saved to {filepath}[/green]")

    if args.stats:
        stats = exporter.get_stats()
        print_stats(stats)

    if args.separate:
        base = filepath.replace(".txt", "")
        files = exporter.export_by_protocol(base, fmt=args.format)
        console.print(f"\n[green][+] Exported by protocol:[/green]")
        for f in files:
            console.print(f"  [dim]- {f}[/dim]")

    return valid_proxies


def print_stats(stats):
    """Print proxy statistics table."""
    console.print("\n[bold]Statistics:[/bold]\n")

    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Proxies", str(stats.get("total", 0)))
    table.add_row("Avg Speed", f"{stats.get('avg_speed_ms', 0)}ms")
    table.add_row("Fastest", f"{stats.get('fastest_ms', 0)}ms")

    protocols = stats.get("protocols", {})
    if protocols:
        proto_str = ", ".join([f"{k}: {v}" for k, v in protocols.items()])
        table.add_row("Protocols", proto_str)

    anonymity = stats.get("anonymity", {})
    if anonymity:
        anon_str = ", ".join([f"{k}: {v}" for k, v in anonymity.items()])
        table.add_row("Anonymity", anon_str)

    countries = stats.get("countries", {})
    if countries:
        country_str = ", ".join([f"{k}: {v}" for k, v in list(countries.items())[:5]])
        table.add_row("Top Countries", country_str)

    console.print(table)


def cmd_info(args):
    """Show available scrapers info."""
    aggregator = ProxyAggregator()
    scrapers = aggregator.get_scrapers_info()

    console.print("[bold]Available Scraper Sources:[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#")
    table.add_column("Source")

    for i, name in enumerate(scrapers, 1):
        table.add_row(str(i), name)

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Professional Proxy Scraper for OpenBullet2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scrape                           Scrape and check all sources
  python main.py scrape --sources freeproxy-list  Use only free-proxy-list
  python main.py scrape --protocol HTTPS          Filter by HTTPS
  python main.py scrape --anonymity elite         Only elite proxies
  python main.py scrape --ob-format               Export in OpenBullet format
  python main.py scrape --threads 200             Use 200 threads for checking
  python main.py scrape --separate                Split by protocol
  python main.py info                             Show available sources
        """,
    )

    parser.add_argument("command", choices=["scrape", "info"], help="Command to run")

    scrape_group = parser.add_argument_group("scrape options")
    scrape_group.add_argument("--sources", nargs="+", help="Specific scrapers to use")
    scrape_group.add_argument("--protocol", choices=["HTTP", "HTTPS", "SOCKS4", "SOCKS5"], help="Filter by protocol")
    scrape_group.add_argument("--anonymity", choices=["elite", "anonymous", "transparent"], help="Filter by anonymity")
    scrape_group.add_argument("--max-speed", type=float, help="Max response time in ms")
    scrape_group.add_argument("--threads", type=int, default=100, help="Threads for checking (default: 100)")
    scrape_group.add_argument("--timeout", type=int, default=10, help="Scrape timeout in seconds (default: 10)")
    scrape_group.add_argument("--check-timeout", type=int, default=5, help="Check timeout in seconds (default: 5)")
    scrape_group.add_argument("--check-anonymity", action="store_true", help="Verify anonymity level during check")
    scrape_group.add_argument("--no-check", action="store_true", help="Skip proxy validation")
    scrape_group.add_argument("--save", default="proxies.txt", help="Output file path (default: proxies.txt)")
    scrape_group.add_argument("--save-checked", help="Output file for checked proxies")
    scrape_group.add_argument("--format", choices=["ip:port", "protocol://ip:port", "ip:port:protocol", "ip:port:country", "openbullet", "ip:port:user:pass"], default="ip:port", help="Proxy format")
    scrape_group.add_argument("--ob-format", action="store_true", help="Export in OpenBullet format (PROTOCOL|IP:PORT)")
    scrape_group.add_argument("--separate", action="store_true", help="Export separate files by protocol")
    scrape_group.add_argument("--stats", action="store_true", help="Show proxy statistics")
    scrape_group.add_argument("--limit", type=int, help="Limit number of proxies to save")

    args = parser.parse_args()

    print_banner()

    if args.command == "info":
        cmd_info(args)
    elif args.command == "scrape":
        cmd_scrape(args)


if __name__ == "__main__":
    main()
