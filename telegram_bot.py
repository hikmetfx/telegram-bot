import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"

def get_openrouter_response(user_message: str, auth_token: str) -> str:
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Telegram Bot",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Sen Azerbaycan dilinde cavab veren AI komekcsisen. Her zaman Azerbaycan dilinde cavab ver."},
            {"role": "user", "content": user_message}
        ],
    }
    try:
        resp = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Xeta: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Salam! Mən AI botam. Sualınızı yazın!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not auth_token:
        await update.message.reply_text("API açarı tapılmadı.")
        return
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    response = get_openrouter_response(user_message, auth_token)
    await update.message.reply_text(response)

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN tapılmadı.")
        return
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot başladı.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
