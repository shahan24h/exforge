import asyncio
import os
import sys
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.maps_scraper      import scrape_google_maps, save_to_csv
from database.db               import init_db, insert_lead, get_stats
from shortlister.shortlist     import run_shortlister
from approvals.approval_gate   import run_approval_gate
from auditor.audit             import run_auditor
from reporter.report_generator import run_report_generator
from emailer.compose           import run_email_composer
from approvals.approval_gate2  import run_approval_gate2
from emailer.send              import run_sender

# ── CONFIG ──────────────────────────────────────────────
SEARCH_QUERIES = [
    ("restaurants",       "New York, NY"),
    ("cleaning services", "New York, NY"),
    ("plumbers",          "New York, NY"),
]
MAX_RESULTS  = 30
RUN_TIME     = "09:00"  # run daily at 9am
# ────────────────────────────────────────────────────────


async def scrape_phase():
    """Phase 1 — Scrape Google Maps and store in DB."""
    print("\n" + "="*60)
    print("  PHASE 1 — Scraping Google Maps")
    print("="*60)

    init_db()

    for query, location in SEARCH_QUERIES:
        print(f"\n[+] Scraping: {query} in {location}")
        data = await scrape_google_maps(query, location, MAX_RESULTS)
        save_to_csv(data, query, location)

        inserted = 0
        skipped  = 0
        for business in data:
            if insert_lead(business):
                inserted += 1
            else:
                skipped += 1

        print(f"[✓] {inserted} new, {skipped} duplicates skipped")

    get_stats()


def run_pipeline():
    """Run the full agent pipeline."""
    print("\n" + "="*60)
    print(f"  EXFORGE AGENT — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)

    # ── Phase 1: Scrape ──
    asyncio.run(scrape_phase())

    # ── Phase 2: AI Shortlist ──
    print("\n" + "="*60)
    print("  PHASE 2 — AI Shortlisting")
    print("="*60)
    run_shortlister()

    # ── Phase 3: Human Approval Gate #1 ──
    print("\n" + "="*60)
    print("  PHASE 3 — Human Approval Gate #1")
    print("="*60)
    run_approval_gate()

    # ── Phase 4: Website Audit ──
    print("\n" + "="*60)
    print("  PHASE 4 — Website Auditor")
    print("="*60)
    asyncio.run(run_auditor())

    # ── Phase 5: Report Generation ──
    print("\n" + "="*60)
    print("  PHASE 5 — Report Generator")
    print("="*60)
    run_report_generator()

    # ── Phase 6: Email Composition ──
    print("\n" + "="*60)
    print("  PHASE 6 — Email Composer")
    print("="*60)
    run_email_composer()

    # ── Phase 7: Human Approval Gate #2 ──
    print("\n" + "="*60)
    print("  PHASE 7 — Human Approval Gate #2")
    print("="*60)
    run_approval_gate2()

    # ── Phase 8: Send Emails ──
    print("\n" + "="*60)
    print("  PHASE 8 — Sending Emails")
    print("="*60)
    asyncio.run(run_sender())

    print("\n" + "="*60)
    print(f"  CYCLE COMPLETE — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    get_stats()


def start_scheduler():
    """Schedule the pipeline to run daily."""
    print(f"[+] Scheduler started — running daily at {RUN_TIME}")
    print(f"[+] Press Ctrl+C to stop\n")

    schedule.every().day.at(RUN_TIME).do(run_pipeline)

    # Also run immediately on start
    print("[+] Running pipeline now...\n")
    run_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ExForge Lead Gen Agent")
    parser.add_argument("--now",       action="store_true", help="Run pipeline once immediately")
    parser.add_argument("--schedule",  action="store_true", help="Run on daily schedule")
    parser.add_argument("--scrape",    action="store_true", help="Run scraper only")
    parser.add_argument("--shortlist", action="store_true", help="Run shortlister only")
    parser.add_argument("--audit",     action="store_true", help="Run auditor only")
    parser.add_argument("--report",    action="store_true", help="Run report generator only")
    parser.add_argument("--compose",   action="store_true", help="Run email composer only")
    parser.add_argument("--send",      action="store_true", help="Run email sender only")
    args = parser.parse_args()

    if args.schedule:
        start_scheduler()
    elif args.now:
        run_pipeline()
    elif args.scrape:
        asyncio.run(scrape_phase())
    elif args.shortlist:
        run_shortlister()
    elif args.audit:
        asyncio.run(run_auditor())
    elif args.report:
        run_report_generator()
    elif args.compose:
        run_email_composer()
    elif args.send:
        asyncio.run(run_sender())
    else:
        print("ExForge Lead Gen Agent")
        print("\nUsage:")
        print("  python main.py --now          # run full pipeline once")
        print("  python main.py --schedule     # run daily at 9am")
        print("  python main.py --scrape       # scrape only")
        print("  python main.py --shortlist    # shortlist only")
        print("  python main.py --audit        # audit only")
        print("  python main.py --report       # report only")
        print("  python main.py --compose      # compose only")
        print("  python main.py --send         # send only")