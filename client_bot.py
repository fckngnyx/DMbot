import asyncio
from aiogram import Bot, Dispatcher, types
import config
import json
import time

bot = Bot(token=config.CLIENT_BOT_TOKEN)
dp = Dispatcher(bot)

# Загружаем данные о магазинах
def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Загружаем данные о статистике
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Сохраняем данные о статистике
def save_data(data):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

async def send_reminder():
    while True:
        users = load_users()
        for user_id in users:
            try:
                await bot.send_message(user_id, "⏰ Напоминаем: Пожалуйста, отправьте данные о вашем обороте.")
            except Exception as e:
                print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
        await asyncio.sleep(3600)  # Отправляем напоминание раз в час

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users:
        return await message.reply("🚫 Ваш магазин не зарегистрирован. Пожалуйста, обратитесь к администратору.")
    
    await message.reply("👋 Привет! Пожалуйста, отправьте данные о вашем обороте.")


async def on_startup(dp):
    asyncio.create_task(send_reminder())  # <-- запуск напоминаний здесь

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)


# Обработка данных от магазина (КК и СБП)
@dp.message_handler(lambda message: message.text.startswith("КК") or message.text.startswith("СБП"))
async def handle_data(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users:
        return await message.reply("🚫 Ваш магазин не зарегистрирован. Пожалуйста, обратитесь к администратору.")
    
    data = load_data()

    if message.text.startswith("КК"):
        # Записываем оборот по КК
        data[user_id] = data.get(user_id, {})
        data[user_id]["КК"] = message.text.split(":")[1].strip()
    elif message.text.startswith("СБП"):
        # Записываем оборот по СБП
        data[user_id] = data.get(user_id, {})
        data[user_id]["СБП"] = message.text.split(":")[1].strip()

    save_data(data)

    # Подтверждение получения данных
    await message.reply(f"✅ Данные для вашего магазина ({users[user_id]['name']}) сохранены.\n"
                         f"КК: {data[user_id].get('КК', 'не указано')}\nСБП: {data[user_id].get('СБП', 'не указано')}\n"
                         f"Спасибо за отправку! Обновите данные, если они изменятся.")

