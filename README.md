# ExForge — AI Lead Generation Agent

Automated pipeline to find, audit, and reach out to small businesses for PixelForge.

---

## Modules
- [x] Scraper — Google Maps business scraper (Playwright)
- [ ] Database — SQLite storage with duplicate prevention
- [ ] AI Shortlist — Claude Haiku lead scoring
- [ ] Human Approval Gate #1 — CLI review
- [ ] Website Auditor — Playwright + Lighthouse
- [ ] Report Generator — PDF with scorecard, competitor comparison
- [ ] Email Composer — AI personalized emails via Claude
- [ ] Human Approval Gate #2 — Draft review
- [ ] Email Sender — SMTP via PixelForge business email
- [ ] Scheduler — Daily cron loop

---

## Tech Stack
- Python 3.13
- Playwright (headless browser)
- SQLite / Supabase
- Claude API (Haiku)
- SMTP (Zoho Mail / PixelForge domain)

---

## Known Improvements (TODO)
- [ ] **Stealth scraping** — replace current Playwright setup with `playwright-stealth`
  to hide automation fingerprints, rotate user agents, and avoid Google detection.
  Install: `pip install playwright-stealth`
  Reference: https://github.com/AtuboDad/playwright_stealth
  Apply in `scraper/maps_scraper.py` inside `async with async_playwright()` block:
```python
  from playwright_stealth import stealth_async
  await stealth_async(page)
```
- [ ] Add random delays between requests (2–5 seconds)
- [ ] Rotate user agents per session
- [ ] Proxy support for high volume scraping

---

## Setup
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## Usage
```bash
python scraper/maps_scraper.py
```

---

## Docker (coming after all modules complete)
Full containerization with Playwright official Docker image:
`mcr.microsoft.com/playwright/python`