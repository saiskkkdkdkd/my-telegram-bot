import os
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

app = Flask(__name__)

# Ваши данные (будут из переменных окружения)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = os.environ.get('YOUR_CHAT_ID')

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        user_info = f"👤 Сообщение от: {user.first_name}"
        if user.last_name:
            user_info += f" {user.last_name}"
        user_info += f"\nID: {user.id}"
        if user.username:
            user_info += f"\n@{user.username}"
        
        # Пересылаем сообщение вам
        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"{user_info}\n\n📨 Текст:\n{update.message.text}"
        )
        
        # Отправляем подтверждение пользователю
        await update.message.reply_text("✅ Ваше сообщение отправлено! Скоро с вами свяжутся.")
        
    except Exception as e:
        print(f"Ошибка: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я бот-помощник. Напишите ваше сообщение, и я перешлю его администратору.")

def setup_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
    return application

# Запуск бота
if __name__ == "__main__":
    bot_app = setup_bot()
    bot_app.run_polling()

@app.route('/')
def home():
    return "Бот работает! 🚀"

# Для вебхука (Heroku)
@app.route('/setwebhook')
def set_webhook():
    bot_app = setup_bot()
    url = f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com/"
    bot_app.bot.set_webhook(url + "webhook")
    return "Webhook установлен!"

@app.route('/webhook', methods=['POST'])
def webhook():
    bot_app = setup_bot()
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.process_update(update)
    return "ok"