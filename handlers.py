from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import (
    add_user, increment_messages, is_blocked, get_admins,
    block_user, unblock_user, remove_admin, stats
)
from config import (
    SUPER_OWNER_ID, AUTO_REPLY, HEADER, TRIGGERS
)
from utils import typing_effect, format_report


# ------------------ USER MESSAGE HANDLER ------------------ #
async def handle_user(update, context):
    msg = update.message
    user = msg.from_user
    text = msg.text

    # BLOCK CHECK
    if is_blocked(user.id):
        return

    # ADD/UPDATE USER
    add_user(user.id, user.username, user.full_name)
    increment_messages(user.id)

    # AUTO REPLY
    await typing_effect(context.bot, user.id)
    await msg.reply_text(AUTO_REPLY)

    # REPORT TO OWNER + ADMINS
    report = format_report(HEADER, user, text)

    # OWNER
    await context.bot.send_message(SUPER_OWNER_ID, report)

    # ADMINS
    for admin in get_admins():
        await context.bot.send_message(admin, report, reply_markup=admin_buttons(user.id))


# ------------------ INLINE BUTTONS ------------------ #
def admin_buttons(uid):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Reply 💌", callback_data=f"reply:{uid}"),
            InlineKeyboardButton("Seen ✔", callback_data=f"seen:{uid}")
        ],
        [
            InlineKeyboardButton("❤️", callback_data=f"react_❤️:{uid}"),
            InlineKeyboardButton("🔥", callback_data=f"react_🔥:{uid}"),
            InlineKeyboardButton("👍", callback_data=f"react_👍:{uid}"),
            InlineKeyboardButton("😂", callback_data=f"react_😂:{uid}")
        ],
        [
            InlineKeyboardButton("Make Admin 👑", callback_data=f"make_admin:{uid}"),
            InlineKeyboardButton("Block ⛔", callback_data=f"block:{uid}")
        ]]
    )


# ------------------ KEYWORD TRIGGERS ------------------ #
async def trigger_system(update, context):
    text = update.message.text.lower()
    for word in TRIGGERS:
        if word in text:
            await typing_effect(context.bot, update.message.chat_id)
            await update.message.reply_text(TRIGGERS[word])
            break


# ------------------ ADMIN / OWNER COMMANDS ------------------ #

async def reply_cmd(update, context):
    user_input = update.message.text.split()
    if len(user_input) < 3:
        return await update.message.reply_text("Format: /reply userID message")

    uid = int(user_input[1])
    msg = " ".join(user_input[2:])
    await typing_effect(context.bot, uid)
    await context.bot.send_message(uid, msg)
    await update.message.reply_text("Reply sent ✔")

async def stats_cmd(update, context):
    total, blocked, admins, owners = stats()
    await update.message.reply_text(
        f"📊 Stats:\nUsers: {total}\nBlocked: {blocked}\nAdmins: {admins}\nOwners: {owners}"
    )


async def block_cmd(update, context):
    uid = int(update.message.text.split()[1])
    block_user(uid)
    await update.message.reply_text("User Blocked ✔")

async def unblock_cmd(update, context):
    uid = int(update.message.text.split()[1])
    unblock_user(uid)
    await update.message.reply_text("User Unblocked ✔")

async def deladmin_cmd(update, context):
    uid = int(update.message.text.split()[1])
    remove_admin(uid)
    await update.message.reply_text("Admin Removed ✔")
