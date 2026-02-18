# استقرار روی سرور رایگان (Oracle Cloud Always Free) + همیشه روشن

این روش واقعاً ۲۴/۷ می‌ماند چون روی VM رایگان اجرا می‌شود و ربات با `systemd` بالا می‌آید.

## 1) ساخت VM رایگان
- در Oracle Cloud ثبت‌نام کن.
- از بخش **Compute** یک **VM.Standard.E2.1.Micro (Always Free)** بساز.
- سیستم‌عامل: Ubuntu 22.04
- یک SSH key اضافه کن.

## 2) آماده‌سازی سرور
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
sudo mkdir -p /opt/z-m-bot
sudo chown -R $USER:$USER /opt/z-m-bot
cd /opt/z-m-bot
git clone <YOUR_REPO_URL> .
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

داخل `.env` مقدارهای واقعی را بگذار:
```env
BOT_TOKEN=توکن_واقعی_ربات
TIMEZONE=Asia/Tehran
ALLOWED_CHAT_IDS=
DB_PATH=/opt/z-m-bot/bot.db
```

## 3) سرویس همیشه روشن
فایل سرویس آماده همین پروژه را نصب کن:
```bash
sudo cp deploy/zmbot.service /etc/systemd/system/zmbot.service
sudo systemctl daemon-reload
sudo systemctl enable zmbot
sudo systemctl start zmbot
```

## 4) بررسی سلامت
```bash
sudo systemctl status zmbot --no-pager
sudo journalctl -u zmbot -f
```

## 5) آپدیت بعدی
```bash
cd /opt/z-m-bot
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart zmbot
```
