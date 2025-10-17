import asyncio
import sys
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    PicklePersistence,
)

# 🔧 Windows event loop fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# === Токен ===
TOKEN = "8215851506:AAGAwCqPLVbZq26H8E60mkgQ2xE-rycP2Bs"

# === Стан діалогу ===
ASK_NAME, ASK_SUBGROUP, MAIN_MENU = range(3)

# === Список дозволених користувачів ===
ALLOWED_USERS = [
    "Бирка Христина",
    "Булига Назарій",
    "Бурба Дарія",
    "Гаврилова Ольга",
    "Галамай Єлизавета",
    "Гончарук Дар'я",
    "Гончарук Анна",
    "Гордієнко Андрій",
    "Дєдух Ілля",
    "Іванів Ангеліна",
    "Іванченко Захар",
    "Калужна Анна",
    "Карська Дар'я",
    "Козак Олена",
    "Матвіїшин Юлія",
    "Медведєва Єлизавета",
    "Мовчан Ростислав",
    "Нисинець Златослава",
    "Павлюк Василь",
    "Плечій Максим",
    "Рудий Любомир",
    "Русинчук Юлія",
    "Садовий Андрій",
    "Слободян Анастасія",
    "Чернишенко Катерина",
    "Яворський Назарій",
    "Яртим Махник Даниїл",
    "Яцків Володимир-Лука",
]

# === Головне меню ===
MAIN_MENU_BUTTONS = [
    ["Переглянути ДЗ", "Записати ДЗ"],
    ["Переглянути викладача"],
]


# === /start — перше привітання ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Слава Ісусу Христу 🕊", callback_data="slava")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вітаю! Натисни кнопку нижче 🕊", reply_markup=reply_markup)


# === Натискання кнопки “Слава Ісусу Христу” ===
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # після натискання — все в одному повідомленні
    await query.edit_message_text(
        "Слава Навіки Богу🙏\n\n"
        "Будь ласка, введи своє прізвище та ім’я (наприклад: Калужна Анна)."
    )

    # встановлюємо стан
    context.user_data["state"] = ASK_NAME


# === Обробка повідомлень ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")

    # --- крок 1: введення імені ---
    if state == ASK_NAME:
        name = update.message.text.strip()
        if name not in ALLOWED_USERS:
            await update.message.reply_text(
                "🚫 Вибач, але доступ до бота заборонено.\n"
                "Будь ласка, введи своє прізвище та ім’я ще раз (наприклад: Калужна Анна)."
            )
            # залишаємо стан ASK_NAME — чекаємо нового введення
            context.user_data["state"] = ASK_NAME
            return

        context.user_data["name"] = name
        context.user_data["state"] = ASK_SUBGROUP

        await update.message.reply_text(
            f"✅ Вітаю, {name}!\n\nВибери свою підгрупу:",
            reply_markup=ReplyKeyboardMarkup(
                [["1 підгрупа", "2 підгрупа"]],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return

    # --- крок 2: вибір підгрупи ---
    elif state == ASK_SUBGROUP:
        subgroup = update.message.text.strip()
        if subgroup not in ["1 підгрупа", "2 підгрупа"]:
            await update.message.reply_text("Будь ласка, вибери варіант з клавіатури.")
            return

        context.user_data["subgroup"] = subgroup
        context.user_data["state"] = MAIN_MENU

        await update.message.reply_text(
            f"Підгрупу '{subgroup}' збережено ✅",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
        )
        await update.message.reply_text("Оберіть дію з головного меню 👇")
        return

    # --- крок 3: головне меню ---
    elif state == MAIN_MENU:
        text = update.message.text.strip()
        if text in ["Переглянути ДЗ", "Записати ДЗ", "Переглянути викладача"]:
            await update.message.reply_text(f"🔧 Функція '{text}' ще в розробці.")
        else:
            await update.message.reply_text("Будь ласка, вибери дію з меню 👇")

    else:
        await update.message.reply_text("Напиши /start, щоб почати роботу з ботом.")


# === /cancel ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Розмову перервано. Щоб почати знову, напиши /start.")


# === Основна функція ===
def main():
    persistence = PicklePersistence(filepath="bot_data.pkl")
    app = ApplicationBuilder().token(TOKEN).persistence(persistence).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущено. Натисни Ctrl+C для зупинки.")
    app.run_polling()


if __name__ == "__main__":
    main()
