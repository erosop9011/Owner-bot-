import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from config import BOT_TOKEN
from handlers import (
    handle_user, reply_cmd, stats_cmd,
    block_cmd, unblock_cmd, deladmin_cmd,
    trigger_system
)
from callbacks import button_handler

logging.basicConfig(level=logging.INFO)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # COMMANDS
    app.add_handler(CommandHandler("reply", reply_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("block", block_cmd))
    app.add_handler(CommandHandler("unblock", unblock_cmd))
    app.add_handler(CommandHandler("deladmin", deladmin_cmd))

    # CALLBACK BUTTON HANDLER
    app.add_handler(CallbackQueryHandler(button_handler))

    # MESSAGE + TRIGGERS
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), trigger_system))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user))

    app.run_polling()

if __name__ == "__main__":
    main()
