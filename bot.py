import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))  # Owner Telegram ID

# Escape markdown V2
def escape_md(text: str):
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for c in chars:
        text = text.replace(c, "\\" + c)
    return text

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Welcome to the Anonymous Messaging Bot ✨\nSend your message anytime.")

# Owner reply handler
async def owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return  # Only owner allowed

    if not update.message.reply_to_message:
        return

    # Extract original User ID
    try:
        original = update.message.reply_to_message.text.split("User ID: ")[1].split("\n")[0]
        user_id = int(original)
    except:
        await update.message.reply_text("❌ Cannot detect original user.")
        return

    reply_msg = update.message.text
    await context.bot.send_message(user_id, reply_msg)

    await update.message.reply_text("✔ Replied to user!")

# Handle all user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or ""

    safe_text = escape_md(text)

    delivered = (
        "✨ *New Message Received* ✨\n\n"
        f"👤 *Name:* {escape_md(user.first_name)}\n"
        f"🔗 *Username:* @{escape_md(user.username or 'N/A')}\n"
        f"🆔 *User ID:* `{user.id}`\n"
        f"💬 *Message:*\n{safe_text}\n"
    )

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=delivered,
        parse_mode="MarkdownV2"
    )

    # Confirmation to user
    await update.message.reply_text("Owner will reply soon 💌")

# Broadcast command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    msg = " ".join(context.args)

    if not msg:
        await update.message.reply_text("❌ Enter broadcast message.")
        return

    count = 0
    for user_id in context.application.user_data:
        try:
            await context.bot.send_message(user_id, msg)
            count += 1
        except:
            pass

    await update.message.reply_text(f"✔ Broadcast sent to {count} users")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.ALL & filters.Regex(".*"), owner_reply))

    # Handle all normal messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
