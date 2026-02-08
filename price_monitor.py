import json
import os
import re
import smtplib
from email.mime.text import MIMEText
import requests
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Browser-like headers so Amazon/Flipkart don't block us
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def load_config():
    """Read product list from config.json"""
    with open("config.json", "r") as f:
        return json.load(f)


def get_price_amazon(url):
    """Extract price from an Amazon India product page"""
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Amazon shows price in a span with class "a-price-whole"
    price_element = soup.select_one("span.a-price-whole")
    if price_element:
        price_text = price_element.text.replace(",", "").replace(".", "").strip()
        return float(price_text)

    return None


def get_price_flipkart(url):
    """Extract price from a Flipkart product page"""
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    if response.status_code != 200:
        print(f"  Flipkart returned status {response.status_code}")
        return None

    # Use regex to find price pattern (₹XX,XXX) — doesn't depend on CSS classes
    match = re.search(r"₹([\d,]+)", response.text)
    if match:
        price_text = match.group(1).replace(",", "")
        return float(price_text)

    return None


def send_email(subject, body):
    """Send alert email via Gmail SMTP"""
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL")

    if not all([sender, password, recipient]):
        print("  Email not configured (missing env variables), skipping...")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
    print("  Email sent!")


def send_telegram(message):
    """Send alert via Telegram bot"""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not all([bot_token, chat_id]):
        print("  Telegram not configured (missing env variables), skipping...")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})
    print("  Telegram message sent!")


def check_prices():
    """Main function: check all products and send alerts for deals"""
    config = load_config()
    deals = []

    for product in config["products"]:
        print(f"\n--- {product['name']} (Target: ₹{product['target_price']}) ---")

        for source in product["urls"]:
            platform = source["platform"]
            url = source["url"]

            if platform == "amazon":
                price = get_price_amazon(url)
            elif platform == "flipkart":
                price = get_price_flipkart(url)
            else:
                print(f"  Unknown platform: {platform}")
                continue

            if price is None:
                print(f"  {platform}: Could not fetch price")
            elif price <= product["target_price"]:
                print(f"  {platform}: ₹{price} — DEAL FOUND!")
                deals.append(
                    {
                        "name": product["name"],
                        "platform": platform,
                        "price": price,
                        "target": product["target_price"],
                        "url": url,
                    }
                )
            else:
                print(f"  {platform}: ₹{price} — Above target")

    # Send alerts if any deals found
    if deals:
        message = "🔥 Deal Alert!\n\n"
        for deal in deals:
            message += f"{deal['name']}\n"
            message += (
                f"  {deal['platform']}: ₹{deal['price']} (Target: ₹{deal['target']})\n"
            )
            message += f"  {deal['url']}\n\n"

        print("\n--- Sending alerts ---")
        send_email("Deal Alert! Price dropped!", message)
        send_telegram(message)
    else:
        print("\nNo deals found. Will check again later.")


if __name__ == "__main__":
    check_prices()
