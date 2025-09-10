from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# --- Загружаем данные из JSON-файлов ---
def load_data():
    with open('schedule.json', 'r', encoding='utf-8') as f:
        schedule_data = json.load(f)
    with open('subjects.json', 'r', encoding='utf-8') as f:
        subjects_data = json.load(f)
    return schedule_data['times'], schedule_data['weekly'], subjects_data

schedule_times, weekly_schedule, subjects_info = load_data()

# --- Команды бота ---
from telegram import ReplyKeyboardMarkup, KeyboardButton

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("/schedule"), KeyboardButton("/subject")],
        [KeyboardButton("/day")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        "👋 Привет! Я бот расписания университета. Выбери команду:",
        reply_markup=reply_markup
    )

async def send_schedule_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🔔 Расписание звонков:\n\n"
    for s in schedule_times:
        msg += f"{s['pair']}. ⏰ {s['start']} - {s['end']}\n"
    await update.message.reply_text(msg)

async def send_subject_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите часть названия предмета. Пример: /предмет университет")
        return

    search_term = " ".join(context.args).strip().lower()  # приводим к нижнему регистру
    found_subjects = []

    # Ищем все предметы, в названии которых есть search_term
    for subject_name, info in subjects_info.items():
        if search_term in subject_name.lower():
            found_subjects.append({
                "name": subject_name,
                "cabinet": info["cabinet"],
                "floor": info["floor"],
                "teacher": info["teacher"]
            })

    if not found_subjects:
        await update.message.reply_text(f"❌ Ничего не найдено по запросу: '{search_term}'")
        return

    # Формируем ответ
    if len(found_subjects) == 1:
        subj = found_subjects[0]
        msg = (
            f"📘 {subj['name']}\n"
            f"🚪 Кабинет: {subj['cabinet']}\n"
            f"🏢 Этаж: {subj['floor']}\n"
            f"👨‍🏫 Преподаватель: {subj['teacher']}"
        )
    else:
        msg = f"🔎 Найдено {len(found_subjects)} предмет(ов) по запросу '{search_term}':\n\n"
        for subj in found_subjects:
            msg += (
                f"📘 {subj['name']}\n"
                f"   🚪 {subj['cabinet']}, 🏢 этаж {subj['floor']}\n"
                f"   👨‍🏫 {subj['teacher']}\n\n"
            )

    await update.message.reply_text(msg)

async def send_daily_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите день недели. Пример: /расписание Понедельник")
        return

    day = " ".join(context.args).strip()
    schedule = weekly_schedule.get(day)

    if not schedule:
        await update.message.reply_text(f"❌ Расписание на '{day}' не найдено. Доступны: Пн-Сб.")
        return

    msg = f"📅 {day}\n\n"
    for lesson in schedule:
        pair_num = lesson["pair_num"]
        subject = lesson["subject"]
        time_info = next((t for t in schedule_times if t["pair"] == pair_num), None)
        time_str = f" ({time_info['start']}-{time_info['end']})" if time_info else ""
        msg += f"{pair_num}. {subject}{time_str}\n"

    await update.message.reply_text(msg)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Неизвестная команда. Напиши /start для помощи.")

# --- Запуск бота ---
def main():
    # ❗ ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ @BotFather
    TOKEN = "8293794172:AAFMSj8KXWOsZhJE_Dgsouf47uDqKudIIyY"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("schedule", send_schedule_times))
    application.add_handler(CommandHandler("subject", send_subject_info))
    application.add_handler(CommandHandler("day", send_daily_schedule))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    print("🚀 Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()