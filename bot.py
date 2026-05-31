import os
import asyncio
import random
import json
from datetime import datetime, time
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен возьмём из переменных среды
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://твой-username.github.io/our-world/")
ARISHA_CHAT_ID = int(os.getenv("ARISHA_CHAT_ID", "0"))  # ID Ариши в телеге
TIMEZONE = "Europe/Moscow"  # измени на свой часовой пояс

DATA_FILE = "data.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== РАБОТА С ДАННЫМИ ======
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"start_date": "2024-01-01"}  # дата по умолчанию

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== КОМПЛИМЕНТЫ ======
COMPLIMENTS = [
    # О красоте
    "Ариша, твоя улыбка — это моё личное солнце ☀️ Когда ты улыбаешься, я забываю обо всём.",
    "Твои глаза — самое красивое, что я видел в этой жизни 👁️✨",
    "Ты невероятно красивая. И каждый день — по-новому. 🌸",
    "Иногда я смотрю на тебя и думаю: как мне так повезло? 💖",
    "У тебя самая нежная улыбка во вселенной 🌷",
    "Твои волосы пахнут счастьем, я серьёзно 💆‍♀️",
    "Когда ты смеёшься — у меня внутри будто фейерверк 🎆",
    "Ты выглядишь потрясающе даже когда только проснулась 🌅",
    
    # О доброте
    "Ты самый добрый человек, которого я знаю. И это меняет мой мир 💕",
    "Твоя забота — это то, что согревает меня в любую погоду 🤗",
    "Ариша, в тебе столько света, что его хватает на всех вокруг ✨",
    "Ты делаешь людей рядом счастливее, просто будучи собой 🌼",
    "Твоё сердце — самое большое и тёплое, что я знаю 💗",
    "Ты заботишься обо мне так, что я чувствую себя самым счастливым 💞",
    
    # О доверии и отношениях
    "С тобой я могу быть собой. Это самое ценное, что у меня есть 💑",
    "Я доверяю тебе как никому. И это лучшее чувство в мире 🤝",
    "Ты — мой дом. Не место, а ощущение. 🏡",
    "Каждое утро рядом с тобой — это подарок 🎁",
    "С тобой даже молчать — это счастье. Понимаешь? 🤍",
    "Ты единственная, кому я готов рассказать всё 💌",
    
    # Об уме и характере
    "Ты такая умная, что я иногда теряюсь от восхищения 🧠✨",
    "Твой характер — это смесь нежности и силы. Невероятно. 💪💕",
    "Ты вдохновляешь меня становиться лучше каждый день 🌟",
    "Меня покоряет то, как ты думаешь и видишь мир 🌍",
    "Ты сильнее, чем сама думаешь. Я это вижу. 🦋",
    
    # О чувствах
    "Я люблю тебя. Просто так. Без причин. Очень. 💖",
    "С тобой я понял, что такое настоящее счастье 🥰",
    "Ты — моя любимая часть каждого дня 🌷",
    "Знаешь, я мог бы говорить тебе комплименты вечно — и не устать 💞",
    "Ты — моё «дома». Где бы я ни был. 🏡💕",
    "Спасибо, что выбрала меня. Я каждый день это ценю. 🙏❤️",
    "Я бы выбрал тебя снова. И снова. И снова. 💍",
    
    # Игривые
    "Ариша, ты опасна — слишком красивая 😍 Я мог бы пострадать.",
    "Если бы тебя не существовало, мне пришлось бы тебя выдумать 💭💕",
    "Подозреваю, что ты волшебница. Иначе как объяснить твоё влияние на меня? 🧚‍♀️",
    "Ты — мой любимый человек в этой галактике 🌌 (и в соседних тоже)",
]

# ====== УТРЕННИЕ И НОЧНЫЕ СООБЩЕНИЯ ======
MORNING_TEMPLATES = [
    "Доброе утро, моя {epithet} 🌅\n{message}",
    "🌸 С добрым утром, любимая!\n{message}",
    "Просыпайся, солнышко ☀️\n{message}",
    "Доброе утречко, моя самая красивая 💕\n{message}",
    "🌷 Аришенька, доброе утро!\n{message}",
]

MORNING_EPITHETS = ["принцесса", "красавица", "родная", "любимая", "звёздочка", "нежная", "солнышко"]

MORNING_MESSAGES = [
    "Сегодня будет прекрасный день, потому что в нём есть ты ✨",
    "Пусть утренний кофе будет таким же сладким, как ты 💕",
    "Я уже скучаю по тебе, хоть мы и совсем недавно прощались 🥰",
    "Желаю тебе сегодня улыбаться как можно чаще 😊",
    "Пусть этот день принесёт тебе много радости и нежности 🌸",
    "Помни: ты самая красивая, даже только проснувшись 💖",
    "Сегодня твой день — носи его как корону 👑",
    "Я думаю о тебе. Прямо сейчас. И ещё через минуту тоже. 💭",
    "Пусть сегодня всё будет легко и тепло 🌼",
    "Обнимаю тебя мысленно так крепко-крепко 🤗",
    "Сегодня я снова буду благодарить вселенную за тебя 🙏",
    "Пусть твой день начнётся с улыбки — моей улыбки тебе 😊💕",
]

NIGHT_TEMPLATES = [
    "Спокойной ночи, моя {epithet} 🌙\n{message}",
    "🌌 Сладких снов, любимая!\n{message}",
    "Аришенька, доброй ночи 💤\n{message}",
    "🌙 Засыпай, моя самая нежная\n{message}",
    "Спи сладко, родная 🌷\n{message}",
]

NIGHT_EPITHETS = ["принцесса", "звёздочка", "родная", "любимая", "нежная", "сонечка", "красавица"]

NIGHT_MESSAGES = [
    "Пусть тебе приснится что-то очень доброе и тёплое ✨",
    "Я обнимаю тебя сквозь расстояние. Спи сладко 🤗",
    "Спасибо за этот день. Он был лучше из-за тебя 💕",
    "Засыпай с мыслью о том, как сильно тебя любят 💖",
    "Пусть ночь будет спокойной, а сны — нежными 🌸",
    "Я люблю тебя. Это последнее, что хочу сказать сегодня 💞",
    "Завтра будет ещё один день вместе. И это счастье 🌅",
    "Спи, моя хорошая. Я думаю о тебе. 💭",
    "Пусть тебе приснюсь я. И мы будем счастливы во сне 😴💕",
    "Закрывай глазки, моя девочка. Всё будет хорошо. 🌙",
    "Пусть звёзды охраняют твой сон сегодня ⭐",
    "Доброй ночи, любовь моя. До утра. 🌷",
]

def generate_morning_message():
    template = random.choice(MORNING_TEMPLATES)
    epithet = random.choice(MORNING_EPITHETS)
    message = random.choice(MORNING_MESSAGES)
    return template.format(epithet=epithet, message=message)

def generate_night_message():
    template = random.choice(NIGHT_TEMPLATES)
    epithet = random.choice(NIGHT_EPITHETS)
    message = random.choice(NIGHT_MESSAGES)
    return template.format(epithet=epithet, message=message)

# ====== ХЭНДЛЕРЫ ======
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💖 Открыть наш мир", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="💕 Комплимент", callback_data="compliment")],
        [InlineKeyboardButton(text="📅 Сколько мы вместе", callback_data="days")],
    ])
    await message.answer(
        f"Привет, моя любимая 💖\n\n"
        f"Это твой личный бот. Здесь:\n"
        f"💌 Наш сайт с играми и письмом\n"
        f"💕 Комплименты для тебя\n"
        f"📅 Счётчик наших дней\n\n"
        f"Твой ID: <code>{user_id}</code>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.message(Command("compliment"))
async def cmd_compliment(message: types.Message):
    compliment = random.choice(COMPLIMENTS)
    await message.answer(compliment)

@dp.message(Command("days"))
async def cmd_days(message: types.Message):
    data = load_data()
    start = datetime.strptime(data["start_date"], "%Y-%m-%d")
    today = datetime.now()
    days = (today - start).days
    
    years = days // 365
    months = (days % 365) // 30
    remaining_days = (days % 365) % 30
    
    text = f"💕 <b>Мы вместе уже:</b>\n\n"
    text += f"🌟 <b>{days}</b> дней\n"
    text += f"📅 С {start.strftime('%d.%m.%Y')}\n\n"
    if years > 0:
        text += f"= {years} {'год' if years == 1 else 'года' if years < 5 else 'лет'} "
    if months > 0:
        text += f"{months} мес. "
    if remaining_days > 0:
        text += f"{remaining_days} дн."
    text += "\n\nИ каждый из них — счастье 💖"
    
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("setdate"))
async def cmd_setdate(message: types.Message):
    text = message.text.replace("/setdate", "").strip()
    if not text:
        await message.answer(
            "📅 Чтобы изменить дату, напиши:\n"
            "<code>/setdate ГГГГ-ММ-ДД</code>\n\n"
            "Например: <code>/setdate 2023-06-15</code>",
            parse_mode="HTML"
        )
        return
    try:
        datetime.strptime(text, "%Y-%m-%d")
        data = load_data()
        data["start_date"] = text
        save_data(data)
        await message.answer(f"✅ Дата обновлена: {text} 💕")
    except ValueError:
        await message.answer("❌ Неправильный формат. Используй ГГГГ-ММ-ДД, например: 2023-06-15")

@dp.callback_query(lambda c: c.data == "compliment")
async def cb_compliment(callback: types.CallbackQuery):
    compliment = random.choice(COMPLIMENTS)
    await callback.message.answer(compliment)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "days")
async def cb_days(callback: types.CallbackQuery):
    data = load_data()
    start = datetime.strptime(data["start_date"], "%Y-%m-%d")
    days = (datetime.now() - start).days
    await callback.message.answer(
        f"💕 Мы вместе уже <b>{days}</b> дней!\n"
        f"С {start.strftime('%d.%m.%Y')} 🌷",
        parse_mode="HTML"
    )
    await callback.answer()

# ====== РАСПИСАНИЕ ======
async def send_morning():
    if ARISHA_CHAT_ID:
        try:
            await bot.send_message(ARISHA_CHAT_ID, generate_morning_message())
        except Exception as e:
            print(f"Ошибка утреннего сообщения: {e}")

async def send_night():
    if ARISHA_CHAT_ID:
        try:
            await bot.send_message(ARISHA_CHAT_ID, generate_night_message())
        except Exception as e:
            print(f"Ошибка ночного сообщения: {e}")

# ====== ЗАПУСК ======
async def main():
    scheduler = AsyncIOScheduler(timezone=ZoneInfo(TIMEZONE))
    scheduler.add_job(send_morning, "cron", hour=10, minute=0)
    scheduler.add_job(send_night, "cron", hour=0, minute=0)
    scheduler.start()
    
    print("Бот запущен 💖")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
