# Deal Bot - Project Context

## 🎯 Project Goal

Build a **price monitoring bot** for Amazon India and Flipkart that:
- Checks product prices every 6 hours
- Sends email/Telegram alerts when price drops below target
- Deploys for **free** on GitHub Actions

## 🏗️ Architecture

```
GitHub Actions (runs every 6 hours)
        │
        ▼
Python Script (price_monitor.py)
        │
    ┌───┴───┐
    ▼       ▼
Amazon   Flipkart
(fetch)  (fetch)
    │       │
    └───┬───┘
        ▼
Price <= Target?
    │
  YES → Send Alert (Email/Telegram)
   NO → Wait for next check
```

## 🛠️ Tech Stack

- **Python 3.12+**
- **uv** (NOT pip) - Fast package manager
- **GitHub Actions** - Free deployment, runs on schedule
- **Email (Gmail SMTP)** - Free notifications
- **Telegram** (optional) - Free, instant mobile alerts

## ✅ Completed Steps

1. ✅ `uv init` - Project initialized
   - Created: `pyproject.toml`, `main.py`, `.python-version`, `.gitignore`

## 📋 Next Steps

2. ⏳ Initial git commit
3. ⏳ `uv add requests` - Add HTTP library for fetching pages
4. ⏳ Create `config.json` - Product URLs and target prices
5. ⏳ Write `price_monitor.py` - Main script with:
   - Price extraction for Amazon
   - Price extraction for Flipkart
   - Email notification function
   - Telegram notification function (optional)
6. ⏳ Create `.github/workflows/price-check.yml` - GitHub Actions workflow
7. ⏳ Test locally
8. ⏳ Push to GitHub and configure secrets

## 👤 User Preferences

- **Interactive learning** - Explain each command before running
- **Step-by-step** - Don't dump all code at once
- **Understand the workflow** - User wants to learn how things connect
- **uv over pip** - User prefers uv package manager

## 📁 Project Structure (Planned)

```
deal-bot/
├── CLAUDE.md           # This context file
├── pyproject.toml      # Dependencies (managed by uv)
├── uv.lock             # Lock file (auto-generated)
├── .python-version     # Python 3.12
├── .gitignore          # Ignore venv, cache, secrets
├── config.json         # Product URLs + target prices
├── price_monitor.py    # Main script
├── README.md           # Setup instructions
└── .github/
    └── workflows/
        └── price-check.yml  # GitHub Actions (runs every 6 hours)
```

## 🔧 Commands Reference

```bash
# Add dependency
uv add <package>

# Run script
uv run python price_monitor.py

# Sync dependencies
uv sync
```

## 🔑 Secrets Needed (for GitHub Actions)

| Secret | Purpose |
|--------|---------|
| `SENDER_EMAIL` | Gmail address to send from |
| `SENDER_PASSWORD` | Gmail app password (not regular password) |
| `RECIPIENT_EMAIL` | Email to receive alerts |
| `TELEGRAM_BOT_TOKEN` | (Optional) Telegram bot token |
| `TELEGRAM_CHAT_ID` | (Optional) Your Telegram chat ID |
