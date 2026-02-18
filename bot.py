from __future__ import annotations

import logging
import os
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from messages import random_quote, relationship_days_text
from storage import Database
from utils import parse_hhmm

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tehran")
ALLOWED_CHAT_IDS_RAW = os.getenv("ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS = {
    int(item.strip())
    for item in ALLOWED_CHAT_IDS_RAW.split(",")
    if item.strip().isdigit()
}

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required. Put it in .env")



def is_chat_allowed(chat_id: int) -> bool:
    return not ALLOWED_CHAT_IDS or chat_id in ALLOWED_CHAT_IDS


def require_allowed_chat(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if not chat:
            return
        if not is_chat_allowed(chat.id):
            await update.effective_message.reply_text(
                "⛔ این چت برای استفاده از ربات مجاز نیست."
            )
            return
        return await func(update, context)

    return wrapper


async def send_daily_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    chat_id = context.job.chat_id
    if chat_id is None:
        return
    chat = db.get_chat(chat_id)
    if not chat:
        return
    await context.bot.send_message(chat_id=chat_id, text=random_quote(chat.your_name, chat.partner_name))


def job_name(chat_id: int) -> str:
    return f"daily_{chat_id}"


def schedule_daily(application: Application, chat_id: int, hhmm: str) -> None:
    scheduler: AsyncIOScheduler = application.bot_data["scheduler"]
    hour, minute = parse_hhmm(hhmm)

    scheduler.remove_job(job_name(chat_id)) if scheduler.get_job(job_name(chat_id)) else None

    scheduler.add_job(
        send_daily_message,
        "cron",
        id=job_name(chat_id),
        hour=hour,
        minute=minute,
        timezone=pytz.timezone(TIMEZONE),
        kwargs={"context": application},
    )


async def run_daily_message_from_scheduler(application: Application, chat_id: int) -> None:
    db: Database = application.bot_data["db"]
    chat = db.get_chat(chat_id)
    if chat:
        await application.bot.send_message(
            chat_id=chat_id,
            text=random_quote(chat.your_name, chat.partner_name),
        )


def configure_scheduler(app: Application, db: Database) -> None:
    scheduler = AsyncIOScheduler(timezone=pytz.timezone(TIMEZONE))
    app.bot_data["scheduler"] = scheduler

    def _make_job(chat_id: int):
        async def _job():
            await run_daily_message_from_scheduler(app, chat_id)

        return _job

    for chat in db.chats_with_daily_time():
        hour, minute = parse_hhmm(chat.daily_time)
        scheduler.add_job(
            _make_job(chat.chat_id),
            "cron",
            id=job_name(chat.chat_id),
            hour=hour,
            minute=minute,
            timezone=pytz.timezone(TIMEZONE),
        )

    scheduler.start()


@require_allowed_chat
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "سلام عزیزم 🌸\n"
            "برای شروع این دستور رو بزن:\n"
            "/start نام_تو نام_پارتنر\n\n"
            "مثال: /start علی نازنین"
        )
        return

    your_name = context.args[0]
    partner_name = context.args[1]
    chat_id = update.effective_chat.id
    db: Database = context.application.bot_data["db"]
    db.upsert_chat_names(chat_id, your_name, partner_name)

    await update.message.reply_text(
        f"عالیه! ❤️ تنظیم شد برای {your_name} و {partner_name}.\n"
        "دستور /help رو بزن تا امکانات کامل رو ببینی."
    )


@require_allowed_chat
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📌 دستورات ربات عاشقانه:\n\n"
        "/start نام_تو نام_پارتنر - ثبت اولیه\n"
        "/love - یک پیام عاشقانه فوری\n"
        "/daily HH:MM - تنظیم پیام روزانه\n"
        "/stopdaily - توقف پیام روزانه\n"
        "/anniversary YYYY-MM-DD - ثبت تاریخ شروع رابطه\n"
        "/dayslove - نمایش مدت زمان رابطه\n"
        "/note متن - ذخیره یادداشت مشترک\n"
        "/notes - نمایش یادداشت‌ها\n"
        "/delnote ID - حذف یادداشت"
    )


@require_allowed_chat
async def love(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.bot_data["db"]
    chat_id = update.effective_chat.id
    chat = db.get_chat(chat_id)
    if not chat:
        await update.message.reply_text("اول با /start نام‌ها رو ثبت کن 💖")
        return

    await update.message.reply_text(random_quote(chat.your_name, chat.partner_name))


@require_allowed_chat
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text("فرمت صحیح: /daily HH:MM\nمثال: /daily 09:30")
        return

    chat_id = update.effective_chat.id
    db: Database = context.application.bot_data["db"]
    chat = db.get_chat(chat_id)
    if not chat:
        await update.message.reply_text("اول با /start نام‌ها رو ثبت کن 💖")
        return

    hhmm = context.args[0]
    try:
        parse_hhmm(hhmm)
    except ValueError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    db.set_daily_time(chat_id, hhmm)

    scheduler: AsyncIOScheduler = context.application.bot_data["scheduler"]
    if scheduler.get_job(job_name(chat_id)):
        scheduler.remove_job(job_name(chat_id))

    hour, minute = parse_hhmm(hhmm)

    async def _job():
        await run_daily_message_from_scheduler(context.application, chat_id)

    scheduler.add_job(
        _job,
        "cron",
        id=job_name(chat_id),
        hour=hour,
        minute=minute,
        timezone=pytz.timezone(TIMEZONE),
    )

    await update.message.reply_text(
        f"✅ پیام روزانه روی ساعت {hhmm} تنظیم شد (منطقه زمانی: {TIMEZONE})."
    )


@require_allowed_chat
async def stopdaily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    db: Database = context.application.bot_data["db"]
    db.set_daily_time(chat_id, None)

    scheduler: AsyncIOScheduler = context.application.bot_data["scheduler"]
    if scheduler.get_job(job_name(chat_id)):
        scheduler.remove_job(job_name(chat_id))

    await update.message.reply_text("🛑 پیام روزانه متوقف شد.")


@require_allowed_chat
async def anniversary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text(
            "فرمت صحیح: /anniversary YYYY-MM-DD\nمثال: /anniversary 2024-06-01"
        )
        return

    chat_id = update.effective_chat.id
    db: Database = context.application.bot_data["db"]
    chat = db.get_chat(chat_id)
    if not chat:
        await update.message.reply_text("اول با /start نام‌ها رو ثبت کن 💖")
        return

    date_text = context.args[0]
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text("❌ تاریخ نامعتبره. فرمت باید YYYY-MM-DD باشه.")
        return

    db.set_anniversary(chat_id, date_text)
    await update.message.reply_text("✅ تاریخ شروع رابطه ذخیره شد.")


@require_allowed_chat
async def dayslove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    db: Database = context.application.bot_data["db"]
    chat = db.get_chat(chat_id)
    if not chat:
        await update.message.reply_text("اول با /start نام‌ها رو ثبت کن 💖")
        return

    if not chat.anniversary_date:
        await update.message.reply_text("اول با /anniversary تاریخ رابطه رو ثبت کن 🌹")
        return

    start_date = datetime.strptime(chat.anniversary_date, "%Y-%m-%d").date()
    await update.message.reply_text(relationship_days_text(start_date))


@require_allowed_chat
async def note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("فرمت صحیح: /note متن یادداشت")
        return

    chat_id = update.effective_chat.id
    db: Database = context.application.bot_data["db"]
    db.add_note(chat_id, text)
    await update.message.reply_text("📝 یادداشت ذخیره شد.")


@require_allowed_chat
async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    db: Database = context.application.bot_data["db"]
    rows = db.list_notes(chat_id)
    if not rows:
        await update.message.reply_text("یادداشتی ثبت نشده.")
        return

    lines = ["📚 لیست یادداشت‌ها:"]
    for row in rows[:20]:
        lines.append(f"{row['id']}) {row['content']} ({row['created_at']})")

    await update.message.reply_text("\n".join(lines))


@require_allowed_chat
async def delnote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("فرمت صحیح: /delnote ID")
        return

    chat_id = update.effective_chat.id
    note_id = int(context.args[0])
    db: Database = context.application.bot_data["db"]
    deleted = db.delete_note(chat_id, note_id)
    if deleted:
        await update.message.reply_text("🗑 یادداشت حذف شد.")
    else:
        await update.message.reply_text("ID پیدا نشد.")


def main() -> None:
    db = Database(os.getenv("DB_PATH", "bot.db"))

    app = Application.builder().token(BOT_TOKEN).build()
    app.bot_data["db"] = db

    configure_scheduler(app, db)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("love", love))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("stopdaily", stopdaily))
    app.add_handler(CommandHandler("anniversary", anniversary))
    app.add_handler(CommandHandler("dayslove", dayslove))
    app.add_handler(CommandHandler("note", note))
    app.add_handler(CommandHandler("notes", notes))
    app.add_handler(CommandHandler("delnote", delnote))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
