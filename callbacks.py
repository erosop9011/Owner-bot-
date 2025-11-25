from telegram import Update
from telegram.ext import ContextTypes
from database import add_admin, block_user
from config import SUPER_OWNER_ID, HEADER

# CALLBACK HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = int(data.split(":")[1])

    # REPLY Button
    if data.startswith("reply:"):
        await query.message.reply_text(
            f"Reply to user {user_id}:\nUse:\n/reply {user_id} your_message"
        )
        await query.answer("Reply mode")

    # SEEN button
    elif data.startswith("seen:"):
        await context.bot.send_message(user_id, "Seen ✔")
        await query.answer("Marked Seen")

    # REACTIONS
    elif data.startswith("react_"):
        emoji = data.split(":")[0].replace("react_", "")
        await context.bot.send_message(user_id, f"Owner reacted {emoji}")
        await query.answer(f"Sent {emoji}")

    # MAKE ADMIN
    elif data.startswith("make_admin:"):
        add_admin(user_id)
        await query.answer("User promoted to Admin")

    # BLOCK USER
    elif data.startswith("block:"):
        block_user(user_id)
        await query.answer("User Blocked")
