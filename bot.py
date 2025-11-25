import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME")


# ----------------------- START COMMAND -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Welcome to the Anonymous Messaging Bot ✨\n"
        "Send your message anytime."
    )


# ----------------------- HELP COMMAND -----------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Just send any message, and it will be forwarded to the owner."
    )


# ----------------------- MESSAGE FORWARD SYSTEM -----------------------
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    text = update.message.text

    # forward to owner
    msg = (
        "✨ *New Message Received* ✨\n\n"
        f"🧑 Name: {user.first_name}\n"
        f"🔗 Username: @{user.username}\n"
        f"🆔 User ID: {user.id}\n"
        f"💬 Message:\n{text}"
    )

    await context.bot.send_message(chat_id=OWNER_ID, text=msg, parse_mode="Markdown")

    # send confirmation to user
    await update.message.reply_text("Owner will reply soon 💌")


# ----------------------- OWNER REPLY TO USER -----------------------
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner writes like: /reply user_id message"""

    try:
        parts = update.message.text.split(" ", 2)
        user_id = int(parts[1])
        reply_msg = parts[2]

        await context.bot.send_message(chat_id=user_id, text=reply_msg)
        await update.message.reply_text("Message sent successfully ✔️")

    except:
        await update.message.reply_text("Format: /reply userID message")


# ----------------------- MAIN -----------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # owner-only reply
    app.add_handler(CommandHandler("reply", reply_to_user))

    # normal user messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
