# ExForge — AI Lead Generation Agent 🤖

Autonomous pipeline to find small businesses, audit their websites, generate
professional PDF reports, and send personalized cold emails — all on autopilot.

---

## Modules

- [x] Scraper — Google Maps business scraper (Playwright)
- [x] Database — SQLite storage with duplicate prevention
- [x] AI Shortlist — Claude Haiku lead scoring (auto-approved)
- [x] Website Auditor — Playwright screenshot + SEO checks + email extraction
- [x] Report Generator — PDF with scorecard, issues, revenue impact, screenshot
- [x] Email Composer — AI personalized emails via Claude Haiku
- [x] Email Sender — SMTP via business email with PDF attached
- [x] Scheduler — Daily pipeline loop with individual module commands
- [ ] Human Approval Gate — Optional CLI review (bypassed by default)
- [ ] Lighthouse integration — Deep performance auditing

---

## What It Does

ExForge runs a complete lead generation pipeline automatically:

1. **Scrapes Google Maps** — finds small businesses by niche and location
2. **AI Shortlisting** — Claude Haiku scores each lead (1-10), filters chains and franchises
3. **Website Audit** — visits each site, takes screenshot, checks SEO, extracts contact email
4. **PDF Report** — generates a professional audit report per business with:
   - SEO scorecard (A-F grade)
   - Issues found (missing HTTPS, meta tags, alt text etc.)
   - Revenue impact estimate
   - Live website screenshot
5. **Personalized Email** — Claude writes a unique cold email referencing specific issues found
6. **Auto Send** — sends email with PDF report attached via your business email
7. **Database Tracking** — SQLite tracks every lead, prevents duplicates, logs sent emails

---

## Tech Stack

- Python 3.13
- Playwright (headless browser)
- SQLite (lead database with status tracking)
- Claude API (Haiku) — scoring + email generation
- ReportLab — PDF report generation
- SMTP — business email delivery

---

## Setup
```bash
pip install -r requirements.txt
playwright install chromium
```

Create a `.env` file in the root:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
SMTP_HOST=mail.privateemail.com
SMTP_PORT=465
SMTP_USER=you@yourdomain.com
SMTP_PASS=your-email-password
SENDER_NAME=Your Name
```

---

## Usage
```bash
# Run full pipeline once
python main.py --now

# Run on daily schedule at 9am
python main.py --schedule

# Run individual modules
python main.py --scrape       # scrape Google Maps only
python main.py --shortlist    # AI scoring only
python main.py --audit        # website audit only
python main.py --report       # PDF report generation only
python main.py --compose      # email composition only
python main.py --send         # send emails only
python main.py --sent         # show all sent emails
```

Set your target niche in `main.py`:
```python
SEARCH_QUERIES = [
    ("cleaning services", "New York, NY"),
]
```

---

## Project Structure
```
exforge/
├── scraper/
│   └── maps_scraper.py       # Google Maps scraper
├── database/
│   └── db.py                 # SQLite database manager
├── shortlister/
│   └── shortlist.py          # AI lead scoring
├── auditor/
│   └── audit.py              # Website auditor + email extractor
├── reporter/
│   └── report_generator.py   # PDF report generator
├── emailer/
│   ├── compose.py            # AI email composer
│   └── send.py               # SMTP email sender
├── approvals/
│   ├── approval_gate.py      # Optional manual review gate #1
│   └── approval_gate2.py     # Optional manual review gate #2
├── data/
│   ├── screenshots/          # Website screenshots
│   ├── reports/              # Generated PDF reports
│   └── drafts/               # Email drafts
├── main.py                   # Pipeline orchestrator + scheduler
├── .env                      # API keys and credentials
└── requirements.txt
```

---

## Cost

| Item | Cost |
|---|---|
| Claude API (Haiku) | ~$0.20–0.50/day |
| SMTP (business email) | Free |
| Playwright | Free |
| SQLite | Free |
| **Total** | **~$6–15/month** |

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
- [ ] Competitor comparison in PDF reports
- [ ] Follow-up email sequence for no-reply leads
- [ ] Web dashboard to replace CLI approval gates
- [ ] LinkedIn outreach module

---

## Docker (coming soon)

Full containerization with Playwright official Docker image:
`mcr.microsoft.com/playwright/python`

---

## Disclaimer

This tool is for legitimate business outreach only. Always comply
with CAN-SPAM, GDPR, and local email regulations. Only target
businesses where outreach is legally permitted in your region.

---

## Built By

Built by [Shahan Ahmed](https://shahanahmed.com) — Data Scientist and ML Engineer.
Read on medium: https://medium.com/@shahan24h/i-built-an-ai-agent-that-finds-small-businesses-audits-their-websites-and-sends-personalized-cold-69012ff90d90?postPublishedType=repub

Follow the build on [The Shahan Stack](https://youtube.com/@theshahanstack)
