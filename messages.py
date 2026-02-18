from __future__ import annotations

import random
from datetime import date

ROMANTIC_QUOTES = [
    "عشق یعنی هر روز دوباره انتخابت کنم، حتی وقتی دنیا شلوغه.",
    "کنار تو، حتی روزهای معمولی هم تبدیل به خاطره می‌شن.",
    "تو دلیل لبخندهای بی‌دلیل منی.",
    "هر جا باشم، قلبم آدرسش رو بلده: پیش تو.",
    "عشق ما قرار نیست کامل باشه؛ قرار هست واقعی و موندگار باشه.",
    "تو امن‌ترین جای دنیا برای دل منی.",
    "هر روز با تو، یه شروع تازه‌ست.",
    "تو هم‌صحبتِ دل منی، نه فقط گوشِ من.",
    "بین این همه آدم، دلم فقط تو رو انتخاب کرد.",
    "دوستت دارم؛ ساده، عمیق، همیشگی.",
]


def random_quote(your_name: str, partner_name: str) -> str:
    quote = random.choice(ROMANTIC_QUOTES)
    return (
        f"💌 پیام عاشقانه امروز برای {your_name} و {partner_name}:\n\n"
        f"{quote}\n\n"
        "یادتون نره: با یک جمله محبت‌آمیز، روز همدیگه رو قشنگ‌تر کنید 💖"
    )


def relationship_days_text(start_date: date) -> str:
    delta = (date.today() - start_date).days
    if delta < 0:
        return "📅 تاریخی که ثبت کردی هنوز نرسیده؛ لطفاً تاریخ شروع رابطه رو درست وارد کن."

    years = delta // 365
    months = (delta % 365) // 30
    days = (delta % 365) % 30

    return (
        "⏳ مدت زمان عشق شما تا امروز:\n"
        f"- {delta} روز\n"
        f"- حدود {years} سال و {months} ماه و {days} روز\n\n"
        "هر روزی که کنار همید، یک پیروزیه 🌹"
    )
