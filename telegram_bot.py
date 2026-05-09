import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
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
        "messages": [{"role": "user", "content": user_message}],
    }
    try:
        resp = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API error: {e}")
        return f"API error: {e}"
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format: {e}")
        return "Unexpected response from API."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bot is running. Send a message and I will respond via OpenRouter."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not auth_token:
        await update.message.reply_text("ANTHROPIC_AUTH_TOKEN is not set.")
        return

    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    response = get_openrouter_response(user_message, auth_token)
    await update.message.reply_text(response)


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set.")
        return

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
