import json
import logging
from aiogram import Bot, Dispatcher, executor, types
import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# Загрузка пользователей и данных
try:
    with open("users.json", "r", encoding="utf-8") as f:
        USERS = json.load(f)
except FileNotFoundError:
    USERS = {}

try:
    with open("data.json", "r", encoding="utf-8") as f:
        DATA = json.load(f)
except FileNotFoundError:
    DATA = {}

CURRENT_TIME = None

# Команда /set_time
@dp.message_handler(commands=["set_time"])
async def set_time(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        await message.reply("❌ Нет доступа.")
        return
    global CURRENT_TIME
    CURRENT_TIME = message.get_args().strip()
    await message.reply(f"⏰ Время отчёта установлено: {CURRENT_TIME}")

# Команда /send
@dp.message_handler(commands=["send"])
async def handle_send(message: types.Message):
    global CURRENT_TIME
    if not CURRENT_TIME:
        await message.reply("⚠ Время отчёта не установлено.")
        return

    user_id = str(message.from_user.id)
    if user_id not in USERS:
        await message.reply("❌ Вы не зарегистрированы.")
        return

    try:
        _, kk, sbp = message.text.strip().split()
        kk, sbp = float(kk), float(sbp)
    except:
        await message.reply("⚠ Используй: /send <КК> <СБП>")
        return

    store = USERS[user_id]
    if CURRENT_TIME not in DATA:
        DATA[CURRENT_TIME] = {}
    DATA[CURRENT_TIME][store] = {"kk": kk, "sbp": sbp}

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)

    await message.reply("✅ Данные приняты. Следующий отчёт в **:**")

# Команда /report
@dp.message_handler(commands=["report"])
async def report(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        await message.reply("❌ Нет доступа.")
        return

    if not CURRENT_TIME or CURRENT_TIME not in DATA:
        await message.reply("⛔ Данных пока нет.")
        return

    result = f"📊 Отчёт за {CURRENT_TIME}\n\n"
    for store, values in DATA[CURRENT_TIME].items():
        kk, sbp = values["kk"], values["sbp"]
        percent = (sbp / kk) * 100 if kk else 0

        if percent >= 27:
            color = "🟢"
        elif 20 <= percent < 27:
            color = "🟠"
        else:
            color = "🔴"

        result += f"{store}: КК {kk}, СБП {sbp}, Доля: {percent:.1f}% {color}\n"

    await message.reply(result)

# Команда /add_user
@dp.message_handler(commands=["add_user"])
async def add_user(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        await message.reply("❌ Нет доступа.")
        return

    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.reply("⚠ Используй: /add_user <id> <название>")
        return

    new_id, name = parts[1], parts[2]
    USERS[new_id] = name

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(USERS, f, ensure_ascii=False, indent=2)

    await message.reply(f"✅ Пользователь `{new_id}` добавлен как \"{name}\"", parse_mode="Markdown")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
