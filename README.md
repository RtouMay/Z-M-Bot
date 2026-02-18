# ربات تلگرام عاشقانه (برای شما و پارتنرت)

این پروژه یک ربات تلگرام کامل و ساده است که برای یک زوج طراحی شده:

- ارسال پیام عاشقانه فوری با `/love`
- ارسال خودکار پیام عاشقانه روزانه با `/daily HH:MM`
- ذخیره تاریخ شروع رابطه و محاسبه مدت رابطه
- ثبت یادداشت‌های مشترک
- محدودسازی ربات به چت‌های مجاز

---

## 1) نصب سریع

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2) تنظیمات

یک فایل `.env` در کنار `bot.py` بساز (یا از نمونه کپی کن):

```bash
cp .env.example .env
```

سپس مقدارها را داخل `.env` تنظیم کن:

```env
BOT_TOKEN=توکن_ربات_شما
TIMEZONE=Asia/Tehran
ALLOWED_CHAT_IDS=
DB_PATH=bot.db
```

### گرفتن Chat ID
1. به ربات پیام بده.
2. موقتاً `ALLOWED_CHAT_IDS` را خالی بگذار.
3. بعد از اولین استفاده، Chat ID را از لاگ یا ابزارهای ID finder بردار و در `.env` بگذار، مثل:

```env
ALLOWED_CHAT_IDS=123456789,-100222333444
```

> اگر `ALLOWED_CHAT_IDS` خالی باشد، همه چت‌ها مجازند.

---

## 3) اجرا

```bash
python bot.py
```

---

## 4) دستورات ربات

- `/start نام_تو نام_پارتنر`
- `/help`
- `/love`
- `/daily HH:MM`
- `/stopdaily`
- `/anniversary YYYY-MM-DD`
- `/dayslove`
- `/note متن`
- `/notes`
- `/delnote ID`

---

## 5) مثال واقعی شروع

```text
/start علی نازنین
/anniversary 2024-06-01
/daily 09:30
/love
/note امشب با هم فیلم ببینیم 🎬
/notes
```

---

## نکات مهم امنیتی

- توکن را هرگز داخل کد ننویس.
- `.env` را در گیت commit نکن.
- اگر توکن لو رفت، در BotFather فوراً revoke کن و توکن جدید بگیر.

---

## تست

```bash
pytest -q
```

---

## استقرار ۲۴/۷ روی سرور رایگان

برای اجرای دائمی روی Oracle Cloud Always Free (بدون خواب رفتن سرویس) از این راهنما استفاده کن:

- `deploy_oracle_free.md`

فایل سرویس systemd آماده هم داخل پروژه قرار دارد:

- `deploy/zmbot.service`
