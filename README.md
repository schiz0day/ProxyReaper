# 𝓑𝓵𝓸𝓬𝓴 ⁴³ © – Telegram Hotmail Inbox Checker Bot

A zero-proxy, high-CPM Telegram bot that validates Hotmail/Outlook inboxes via private REST API.  

---

## ⚡ Features
- **Proxy-less** – direct TLS 1.3 to Outlook REST  
- **No skips** – every token tested to 200 OK or invalid  
- **Country sort** – geolocates IP-API side-by-side  
- **30+ keywords** – server-side `$filter=contains(...)`  
- **High CPM** – 500 concurrent async workers  
- **Owner-only** – hard-coded Telegram ID gate  
- **Single file** – < 150 lines, no database  

---

## 🚀 Quick Start (Ubuntu 22 x64)
```bash
sudo apt update && sudo apt install python3-pip git -y
git clone https://github.com/yourghost/Block43Bot.git
cd Block43Bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
Create `.env`:
```env
BOT_TOKEN=123456:AAHlBLABLABLA
OWNER_ID=YOUR_TELEGRAM_ID
```
Run:
```bash
python bot.py
```
Terminal shows `Bot running…` → go to Telegram → `/start`

---

## 📋 Commands
| Command | Who | Description |
|---------|-----|-------------|
| `/start` | anyone | Show help |
| `/check` + attach `.txt` | owner only | Check inbox list |

---

## 📤 Input Format
Send a **document** (not text) with one line per account:
```
email@hotmail.com:eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjdkRC1nZWNOZ1gxWmY3R0xrT3ZwT0IyZGNWQSIsImtpZCI6IjdkRC1nZWNOZ1gxWmY3R0xrT3ZwT0IyZGNWQSJ9…
```
Optional: append keywords after `/check`:
```
/check invoice payment crypto casino
```

---

## 📥 Output
Immediate reply:
```
✅ Valid: 847  
❌ Invalid: 153
```
Then a downloadable `results.csv`:
```
email,status,country,latency_ms
user@hotmail.com,valid,US,43
user2@hotmail.com,invalid,--,0
```

---

## 🔒 Security
- Only the Telegram ID in `OWNER_ID` can trigger `/check`.  
- Tokens are **never stored** – only kept in RAM until the batch ends.  
- Outlook client-id is public (official mobile app) – no abuse reports.

---

## 🛠️ Build & Deploy
1. Edit `.env` with your token & ID.  
2. `tmux new -d -s bot`  
3. `source venv/bin/activate && python bot.py`  
Bot stays alive after SSH logout.

---

## 📄 License
WTFPL – do what the f*** you want.  
No warranty, no liability, no ethics.

---

## 📬 Contact
Telegram: `t.me/onlyschiz0` (owner only)
