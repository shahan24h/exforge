# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ExForge is an autonomous lead-gen pipeline for **PixelForgeBD** (a web agency): scrape local
businesses from Google Maps → AI-score them as leads → audit their website → generate a PDF
report → draft a personalized cold email → send it. Everything is orchestrated through a single
SQLite table (`data/leads.db`) where each lead's `status` column drives which pipeline stage
picks it up next.

## Setup

```bash
pip install -r requirements.txt
camoufox fetch        # downloads the patched stealth-Firefox binary used by the auditor
```

`requirements.txt` is missing one package that is actually imported — install it too:
```bash
pip install googlemaps
```
(`pandas` is listed in requirements.txt but not used anywhere; `Pillow`/`requests`/`beautifulsoup4`
mentioned in the README are not used either.)

`playwright` is still a dependency (camoufox is built on top of it), but `playwright install
chromium` is no longer needed — the auditor now drives Camoufox's own Firefox build instead of
Chromium.

A `.env` file (gitignored) must be present in the repo root. **The env vars actually read by the
code** (not all match the README's `.env.example`):

| Var | Used by | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | shortlister, reporter, emailer/compose | Claude Haiku (`claude-haiku-4-5-20251001`) |
| `GOOGLE_MAPS_API_KEY` | scraper/maps_scraper.py | Google Places API via `googlemaps` lib (README claims Playwright-based scraping — it's actually the official API) |
| `SMTP_HOST` (default `mail.privateemail.com`), `SMTP_PORT` (default `465`), `SMTP_USER`, `SMTP_PASS` | emailer/send.py, test_imap.py | Also reused for the IMAP "Sent" folder copy — there are no separate `IMAP_*` vars despite the README |
| `SENDER_NAME` (default `Shahan`) | emailer/send.py | compose.py hardcodes its own `SENDER_NAME = "Atiqul"` — the two are independent |

The README's `.env.example` (`TARGET_NICHE`, `TARGET_LOCATION`, `MAX_LEADS_PER_RUN`, `MIN_AI_SCORE`,
`AUTO_APPROVE`, `FROM_NAME`, `IMAP_*`, `SMTP_PASSWORD`) is aspirational — **none of those are read by
the current code**. Scrape targets are hardcoded in `main.py`'s `SEARCH_QUERIES` list, and the
"shortlist if score >= 7" threshold is hardcoded in the AI prompt in `shortlister/shortlist.py`.

## Common commands

The real CLI (in `main.py`) differs from what the README documents (`--scrape-only`,
`--audit-only`, `--status`, etc. — those flags don't exist). Actual flags:

```bash
python main.py --now                  # run pipeline in a loop until daily email target hit (default 30, max 10 cycles, 60s between)
python main.py --now --target 10      # same, with a custom daily target
python main.py --schedule             # run once immediately, then daily at 09:00 (via `schedule` lib)

# Run a single stage once (operates on whatever leads are in the right status):
python main.py --scrape       # Google Maps -> data/*.csv + leads.db (status: new)
python main.py --shortlist    # AI score 'new' leads -> 'approved' / 'rejected'
python main.py --audit        # Playwright audit 'approved' leads -> 'audited' / 'site_error'
python main.py --report       # PDF for 'audited' leads -> 'report_ready'
python main.py --compose      # draft email for 'report_ready' leads -> 'approved_to_send' / 'email_drafted'
python main.py --send         # SMTP send 'approved_to_send' leads -> 'emailed' / 'email_failed' / 'no_email'

python main.py --sent         # list every lead with status 'emailed'

# Utilities
python reset.py                # one-off DB repair script (edit before reuse — currently hardcodes a specific lead/email fix)
python test_imap.py            # verify SMTP creds can also append to the IMAP "Sent" folder
python database/db.py          # init_db() + print DB stats
run_exforge.bat                 # Windows Task Scheduler entry point; runs `python main.py --now`, logs to data/logs/run_log.txt
```

There is no test suite, linter, or build step in this repo.

## Architecture: the `leads` table is the state machine

`database/db.py` defines `init_db()` with a base schema (`id, name, category, address, phone
UNIQUE, website, rating, reviews, location, status, email, scraped_at, audited_at, emailed_at`).
`phone` is the dedup key — `insert_lead()` silently no-ops on a duplicate phone.

Every later stage **lazily adds its own columns** via `ALTER TABLE ... ADD COLUMN` wrapped in
`try/except` (so it's a no-op once the column exists): `ai_score`, `ai_reason` (shortlister),
`screenshot_path`, `audit_data`, `site_status` (auditor), `email_subject`, `email_body`,
`email_drafted_at` (composer). So the full schema only exists after a complete pipeline run —
don't assume a fresh `init_db()` has every column.

`update_lead_status(phone, status)` is the single transition function every stage calls. The
pipeline is a strict pull-based chain — each module's `get_*_leads()` query selects leads in
exactly one `status` and pushes them to the next:

```
(scraper)        -> status='new'
(shortlister)     'new'          -> 'approved' | 'rejected'
(auditor)         'approved'     -> 'audited' | 'site_error'
(report_generator)'audited'      -> 'report_ready'
(emailer/compose) 'report_ready' -> 'approved_to_send' (email found during audit) | 'email_drafted' (no email, needs manual lookup)
(emailer/send)    'approved_to_send' -> 'emailed' | 'email_failed' | 'no_email'
```

**`approvals/approval_gate.py` ("Gate #1") is dead code under this flow** — it queries for
`status='shortlisted'`, but `shortlister/shortlist.py` never sets that status (it goes straight
to `'approved'`). `approvals/approval_gate2.py` ("Gate #2") is live: it reviews
`status='email_drafted'` leads and promotes them to `'approved_to_send'` or `'rejected'`. Neither
gate is called from `main.py` — they're standalone interactive CLIs (`input()`-driven) meant to be
run manually between pipeline stages.

## Pipeline stages (modules)

- `scraper/maps_scraper.py` — `scrape_google_maps()` hits the Google Places API (text search +
  pagination), `save_to_csv()` dumps a timestamped CSV to `data/` (informational only — the DB is
  the source of truth downstream).
- `shortlister/shortlist.py` — `pre_filter()` rejects leads with no website/phone or rating < 3.0
  before spending an API call; survivors go to `ai_score_lead()` (Claude Haiku, JSON response with
  `score`/`reason`/`shortlist`).
- `auditor/audit.py` — async Playwright driven via **Camoufox** (`AsyncCamoufox`, a stealth-patched
  Firefox build with anti-bot-detection fingerprinting — run `camoufox fetch` once after install
  to download its browser binary). Visits the site, screenshots it to
  `data/screenshots/<SafeName>.png`, runs `extract_email()` (mailto links → `/contact`,
  `/contact-us`, `/about` → regex scan of body text), then re-visits the homepage for SEO checks
  (title, meta description, H1, alt text, HTTPS, viewport meta, visible contact info) producing a
  0–100 `score` and `issues[]` stored as JSON in `audit_data`.
- `reporter/report_generator.py` — Claude Haiku writes a 3-sentence summary, then `reportlab`
  builds a branded PDF to `data/reports/<SafeName>_report.pdf` (score card, custom-drawn bar
  chart, revenue-impact estimate, embedded screenshot).
- `emailer/compose.py` — Claude Haiku writes the email body and a separate subject line, saves a
  `.txt` draft to `data/drafts/<SafeName>_draft.txt` and the subject/body into the DB.
- `emailer/send.py` — sends via `smtplib.SMTP_SSL`, attaches the PDF from
  `data/reports/`, then appends a copy to the IMAP "Sent" folder via `imaplib` (best-effort; note
  `save_to_sent_folder()` has a duplicated/unreachable second `except` block — a latent bug, not a
  documented behavior).

`<SafeName>` everywhere = `name.replace(" ","_").replace("/","_").replace("|","").strip("_")[:30]`
— this exact transform is repeated independently in auditor, reporter, composer, sender, and
approval_gate2, so screenshot/report/draft filenames line up. If you change it, change it
everywhere.

## Branding constants

`AGENCY_NAME`, `AGENCY_WEBSITE`, `AGENCY_EMAIL`, `AGENCY_WHATSAPP`/`WHATSAPP_NUMBER` are hardcoded
independently in both `reporter/report_generator.py` and `emailer/compose.py` (currently
"PixelForgeBD"). Rebranding requires editing both.

## `data/` layout (gitignored, created at runtime)

```
data/leads.db                       # SQLite — the pipeline state machine
data/<query>_<location>_<ts>.csv    # raw scrape dumps (informational)
data/screenshots/<SafeName>.png
data/reports/<SafeName>_report.pdf
data/drafts/<SafeName>_draft.txt
data/logs/run_log.txt               # written by run_exforge.bat
```
