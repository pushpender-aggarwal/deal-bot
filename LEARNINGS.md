# Project Learnings - Deal Bot

This document summarizes all the important concepts and technical details learned while building the deal-bot project.

---

## 1. **uv Package Manager**

### What is uv?
- **Fast Python package manager** written in Rust (alternative to pip)
- Manages dependencies via `pyproject.toml` (modern Python standard)
- Creates lock files (`uv.lock`) for reproducible builds

### Key Commands
```bash
uv init                    # Initialize new Python project
uv add <package>           # Add a dependency (like pip install)
uv sync                    # Install all dependencies from pyproject.toml
uv run python script.py    # Run Python in the project's virtual environment
```

### Why `uv run`?
- Automatically activates the virtual environment (`.venv/`)
- No need to manually run `source .venv/bin/activate`
- Ensures you're using the correct Python version and dependencies

---

## 2. **Environment Variables & Secrets Management**

### The Problem
- **Never commit secrets** (API keys, tokens, passwords) to Git
- If secrets are in your code, anyone who sees the repo can steal them

### The Solution: `.env` Files

#### `.env` (gitignored - contains real secrets)
```bash
SCRAPEOPS_API_KEY=your-actual-key-here
TELEGRAM_BOT_TOKEN=your-actual-token-here
TELEGRAM_CHAT_ID=your-actual-id-here
```

#### `.env.example` (committed - template for others)
```bash
SCRAPEOPS_API_KEY=your-scrapeops-api-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here
```

### Loading Environment Variables in Python

**Library:** `python-dotenv`

**How it works:**
- `load_dotenv()` reads `.env` file from the current directory
- Loads key-value pairs into `os.environ` (system environment variables)
- `os.environ.get("KEY")` retrieves the value (returns None if not found)
- This keeps secrets out of your source code

---

## 3. **GitHub Actions - Free Automated Workflows**

### What is GitHub Actions?
- **Free cloud automation service** from GitHub
- Runs code on GitHub's servers (Ubuntu, Windows, macOS)
- Perfect for scheduled tasks (cron jobs), testing, deployments
- No need to maintain your own server

### Our Use Case
- Run `price_monitor.py` every 12 hours automatically
- Send Telegram alerts when prices drop below target
- Completely free (GitHub provides the compute resources)

### Key Concepts

**Cron Syntax:** `'0 */12 * * *'`
- `0` = minute (0th minute of the hour)
- `*/12` = every 12 hours
- `* * *` = every day, every month, every day of week
- Example: `0 */12 * * *` = 12am and 12pm UTC every day

**workflow_dispatch:**
- Allows manual triggering from GitHub UI (Actions tab)
- Useful for testing without waiting for the schedule

**GitHub Secrets:**
- Store sensitive values: Repo → Settings → Secrets and variables → Actions
- Access in workflow: `${{ secrets.SECRET_NAME }}`
- Never exposed in logs (shows as `***` in output)
- Passed to your script as environment variables

**Environment Variables in Workflows:**
- Set via `env:` section in workflow steps
- Available to your script just like local `.env` file
- Example: `SCRAPEOPS_API_KEY: ${{ secrets.SCRAPEOPS_API_KEY }}`

---

## 4. **Telegram Bot - Free Instant Notifications**

### What is a Telegram Bot?
- Automated account on Telegram that can send/receive messages
- Free API from Telegram (no usage limits for basic features)
- Perfect for alerts and notifications
- Works on mobile, desktop, and web

### Setting Up a Bot

#### Step 1: Create Bot with BotFather
1. Open Telegram and search for **@BotFather** (official bot for creating bots)
2. Send `/newbot` command
3. Choose a display name (e.g., "My Deal Bot")
4. Choose a username ending in "bot" (e.g., "my_deal_bot")
5. BotFather gives you a **bot token** (acts like a password for your bot)

#### Step 2: Get Your Chat ID
1. Send a message to your bot (any message, like "hi")
2. Visit this URL in browser: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id": 123456789}` in the JSON response
4. That number is your **chat ID** (identifies the conversation)

### How Messages Work
- Your Python script makes a POST request to Telegram's API
- Endpoint: `https://api.telegram.org/bot<TOKEN>/sendMessage`
- Requires: `bot_token` (authenticates your bot) and `chat_id` (recipient)
- Message appears instantly on your phone/computer

---

## 5. **Web Scraping & Anti-Bot Protection**

### The Problem
- Amazon and Flipkart **block automated requests** to prevent bots
- They detect:
  - Missing browser headers (User-Agent, Accept-Language)
  - **Cloud server IPs** (AWS, Azure, GitHub Actions) - datacenter IPs
  - Too many requests from same IP (rate limiting)

### Datacenter IPs vs Residential IPs
- **Datacenter IPs:** Used by cloud servers (AWS, GitHub Actions)
  - Easy to detect and block
  - Not associated with real home users
- **Residential IPs:** Real home internet connections
  - Look like normal users browsing
  - Harder to block without affecting real customers

### Solution 1: User-Agent Headers (Local Development)
- Add browser headers to your request
- Pretends to be a real browser (Chrome, Firefox, etc.)
- Works for **local testing** but fails on **cloud servers** (IP still detected)

### Solution 2: ScrapeOps Proxy (Cloud Servers)

**Why needed?**
- GitHub Actions runs on **datacenter IPs** (automatically blocked)
- Need **residential IPs** to look like home users

**How ScrapeOps works:**
1. You send request to ScrapeOps API with your target URL
2. ScrapeOps fetches the page using **residential proxy network**
3. Returns the HTML to you
4. Amazon/Flipkart sees a residential IP, not a datacenter IP

**Our implementation:**
- If `SCRAPEOPS_API_KEY` exists → use ScrapeOps proxy (for GitHub Actions)
- If not → direct request with headers (for local development)

**Key points:**
- ScrapeOps has a **free tier** (1,000 requests/month)
- Must **confirm email** before API works (security measure)
- Essential for avoiding 403/529 errors on cloud servers

---

## 6. **Git Best Practices**

### What to Commit vs. What to Ignore

**Commit:**
- Source code (`*.py`, `*.json`)
- Configuration templates (`.env.example`)
- Documentation (`README.md`, `CLAUDE.md`, `LEARNINGS.md`)
- Dependency definitions (`pyproject.toml`)
- Lock files (`uv.lock`) - ensures reproducible builds

**Never Commit (.gitignore):**
- Secrets (`.env`) - contains real API keys/tokens
- Virtual environments (`.venv/`, `env/`) - generated files
- Cache files (`__pycache__/`, `*.pyc`) - temporary build artifacts
- IDE settings (`.vscode/`, `*.code-workspace`) - personal preferences
- OS files (`.DS_Store` on Mac) - system-specific

### Local Git Configuration

**Setting email for specific repo:**
```bash
git config --local user.email "your@email.com"
```
- Uses different email for this project only
- Doesn't affect global Git config
- Useful if you have personal + work projects

---

## 7. **HTML Parsing with BeautifulSoup**

### Why BeautifulSoup?
- Parses HTML (web page source code) and extracts data
- Uses CSS selectors (same as styling web pages)
- Makes it easy to find specific elements (prices, titles, etc.)

### Amazon Price Extraction
- Amazon shows price in `<span class="a-price-whole">₹45,999</span>`
- Use CSS selector `span.a-price-whole` to find it
- Clean up text: remove commas, periods, whitespace
- Convert to float for comparison

### Flipkart Price Extraction (Regex Fallback)

**Problem:** Flipkart's CSS classes change frequently
- Today: `div.Nx9bqj.CxhGGd`
- Tomorrow: `div.Ab3dFg.Xy7zQw` (random class names)

**Solution:** Use regex pattern matching
- Search for `₹` symbol followed by digits and commas
- Pattern: `₹([\d,]+)` matches `₹45,999` anywhere in HTML
- Doesn't depend on CSS class names
- More resilient to website changes

---

## 8. **JSON Configuration Files**

### Why `config.json`?
- Separate **data** (product URLs, target prices) from **code**
- Easy to add/remove products without touching Python code
- Non-programmers can update prices/URLs

### Design Choice: Nested URLs
- Each product has an array of URLs (Amazon, Flipkart, etc.)
- Avoids repeating product name and target price
- Scalable - easy to add more platforms or products

---

## 9. **Error Handling & HTTP Status Codes**

### Common Status Codes

| Code | Meaning | Our Context |
|------|---------|-------------|
| 200 | OK | Successfully fetched price |
| 403 | Forbidden | ScrapeOps email not confirmed / IP blocked |
| 429 | Too Many Requests | Rate limited (sending requests too fast) |
| 529 | Site Overloaded | Flipkart temporarily blocking requests |

### Why Check Status Codes?
- Prevents crashes when requests fail
- Helps debug issues (is it our code or their server?)
- Can log errors for monitoring

---

## 10. **Project Workflow Summary**

### Local Development
1. Write code in `.py` files
2. Test locally: `uv run python price_monitor.py`
3. Secrets loaded from `.env` file
4. Direct requests work (residential home IP)

### Testing with Telegram Locally (Without .env file)
If you want to test Telegram notifications quickly without creating a `.env` file:

```bash
TELEGRAM_BOT_TOKEN="your-bot-token" TELEGRAM_CHAT_ID="your-chat-id" uv run python price_monitor.py
```

**How it works:**
- Sets environment variables inline (only for this command)
- Useful for quick testing or one-off runs
- Values available to Python via `os.environ.get()`
- Secrets are NOT saved (disappear after command finishes)

**When to use:**
- Quick testing of Telegram integration
- Running in environments where `.env` file doesn't exist
- Temporary overrides for specific runs

### GitHub Actions Deployment
1. Push code to GitHub
2. Add secrets in repo settings (Settings → Secrets → Actions)
3. Workflow runs on schedule (cron)
4. Secrets passed as environment variables
5. Script uses ScrapeOps proxy (datacenter IP → residential IP)
6. Sends Telegram alerts if price drops

---

## 11. **Key Takeaways**

### Security
- **Never hardcode secrets** in source code
- Use `.env` for local development
- Use GitHub Secrets for cloud deployment
- Always add `.env` to `.gitignore`

### Automation
- GitHub Actions = **free cron jobs** in the cloud
- No need to keep your computer running 24/7
- Perfect for scheduled tasks (monitoring, backups, reports)

### Web Scraping
- **Residential proxies** (ScrapeOps) essential for cloud servers
- **Regex fallback** more resilient than CSS selectors
- Always handle HTTP errors gracefully

### Package Management
- `uv` is **faster** than pip (written in Rust)
- `uv run` handles virtual environments automatically
- Lock files ensure **reproducible builds** across machines

### Communication
- Telegram bots are **free, instant, and mobile-friendly**
- Better than email for real-time alerts
- No need to set up email servers or app passwords

---

## 12. **Debugging Tips**

### Common Issues We Faced

| Problem | Cause | Solution |
|---------|-------|----------|
| "Could not fetch price" | Anti-bot blocking | Use ScrapeOps proxy |
| Flipkart 529 | Rate limiting | Wait between requests / use proxy |
| ScrapeOps 403 | Email not confirmed | Check email, click confirmation link |
| GitHub Actions fails | Missing secrets | Add secrets in repo settings |
| Workflow not running | Wrong cron syntax | Validate at crontab.guru |
| Local script fails | `.env` not loaded | Check `load_dotenv()` is called |

---

## 13. **Resources**

- **uv documentation:** https://docs.astral.sh/uv/
- **GitHub Actions:** https://docs.github.com/en/actions
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **ScrapeOps:** https://scrapeops.io/docs/
- **Cron syntax validator:** https://crontab.guru/
- **BeautifulSoup docs:** https://www.crummy.com/software/BeautifulSoup/

---

**Project completed on:** 2026-02-08
**Key technologies:** Python, uv, GitHub Actions, Telegram Bot, ScrapeOps, BeautifulSoup
