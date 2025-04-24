from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
import config
import json

bot = Bot(token=config.ADMIN_BOT_TOKEN)
dp = Dispatcher(bot)

# Загружаем данные о магазинах
def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Сохраняем данные о магазинах
def save_users(users):
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

# Загружаем данные о статистике
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        return await message.reply("⛔ Доступ запрещён.")
    await message.reply("👋 Привет, администратор!\n\nВыберите команду:")

@dp.message_handler(commands=["add_shop"])
async def add_shop(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        return await message.reply("⛔ Доступ запрещён.")
    await message.reply("💬 Напишите ID магазина, которого вы хотите добавить:")

@dp.message_handler(commands=["remove_shop"])
async def remove_shop(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        return await message.reply("⛔ Доступ запрещён.")
    await message.reply("💬 Напишите ID магазина, которого вы хотите удалить:")

@dp.message_handler(commands=["view_shops"])
async def view_shops(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        return await message.reply("⛔ Доступ запрещён.")
    
    users = load_users()
    if users:
        shops = "\n".join([f"ID: {shop}" for shop in users])
        await message.reply(f"🛒 Список магазинов:\n{shops}")
    else:
        await message.reply("🚫 Нет добавленных магазинов.")

@dp.message_handler(commands=["generate_report"])
async def generate_report(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        return await message.reply("⛔ Доступ запрещён.")
    
    users = load_users()
    data = load_data()

    if users and data:
        report = ""
        for shop_id, shop_data in users.items():
            kk = data.get(shop_id, {}).get("КК", 0)
            sbp = data.get(shop_id, {}).get("СБП", 0)
            if kk != 0:
                # Расчёт доли выполнения плана СБП от КК
                ratio = (sbp / kk) * 100
                if ratio > 27:
                    color = "🟢"
                elif 20 <= ratio <= 27:
                    color = "🟠"
                else:
                    color = "🔴"
                
                report += f"Магазин {shop_data['name']}:\n"
                report += f"КК: {kk}\nСБП: {sbp}\nДоля: {ratio:.2f}% {color}\n\n"
        
        if report:
            await message.reply(f"📊 Отчёт по всем магазинам:\n\n{report}")
        else:
            await message.reply("🚫 Нет данных для отчёта.")
    else:
        await message.reply("🚫 Нет данных для отчёта.")

@dp.message_handler(lambda message: message.text.isdigit())
async def handle_add_remove(message: types.Message):
    if str(message.from_user.id) not in config.ADMIN_IDS:
        return await message.reply("⛔ Доступ запрещён.")
    
    user_id = message.text
    users = load_users()

    # Добавление магазина
    if message.command == "/add_shop":
        if user_id not in users:
            users[user_id] = {"name": "Магазин без имени"}  # Для примера, можно добавлять имя
            save_users(users)
            await message.reply(f"✅ Магазин с ID {user_id} добавлен.")
        else:
            await message.reply(f"🚫 Магазин с ID {user_id} уже существует.")

    # Удаление магазина
    elif message.command == "/remove_shop":
        if user_id in users:
            del users[user_id]
            save_users(users)
            await message.reply(f"✅ Магазин с ID {user_id} удалён.")
        else:
            await message.reply(f"🚫 Магазина с ID {user_id} не найдено.")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
