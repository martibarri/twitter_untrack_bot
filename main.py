from os import getenv
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from ptbcontrib import extract_urls
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Telegram bot that removes the tracking query parameter `t` on Twitter urls\.",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await update.message.reply_text(
        "The bot must be an admin and have the `Delete messages` permission to work on groups\.",
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def remove_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the tracking query parameter 't' on Twitter urls."""
    try:
        urls = extract_urls.extract_urls(update.message)
    except Exception:
        urls = []
    if urls:
        edited = False
        message = update.message.text
        for u in urls:
            if "twitter.com" in u:
                try:
                    _u = urlparse(u)
                    if parse_qs(_u.query).get("t"):
                        message = message.replace(u, _u._replace(query="t=").geturl())
                        edited = True
                except Exception:
                    pass
        if edited:
            await update.message.delete()
            await context.application.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=f"{update.effective_user.name}:"
            )
            await context.application.bot.send_message(
                chat_id=update.effective_message.chat_id, text=message
            )


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Help command
    application.add_handler(CommandHandler("help", help_command))

    # Process TEXT messages
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, remove_tracking)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
