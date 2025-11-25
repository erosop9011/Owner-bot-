import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# CONFIG
# ==============================
OWNER_ID = 5691270692   # Your ID
BOT_TOKEN = "8062849180:AAE62KY0eF-EClrP8l8dtyeo9irYaGXOjjQ"


# ==============================
# DATABASE
# ==============================
conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    fullname TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS blocked (
    user_id INTEGER PRIMARY KEY
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)""")

conn.commit()


# ==============================
# HELPERS
# ==============================
def add_user(uid, username, fullname):
    cur.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (uid, username, fullname))
    conn.commit()

def block_user(uid):
    cur.execute("INSERT OR REPLACE INTO blocked VALUES (?)", (uid,))
    conn.commit()

def unblock_user(uid):
    cur.execute("DELETE FROM blocked WHERE user_id=?", (uid,))
    conn.commit()

def is_blocked(uid):
    cur.execute("SELECT 1 FROM blocked WHERE user_id=?", (uid,))
    return cur.fetchone() is not None

def add_admin(uid):
    cur.execute("INSERT OR REPLACE INTO admins VALUES (?)", (uid,))
    conn.commit()

def remove_admin(uid):
    cur.execute("DELETE FROM admins WHERE user_id=?", (uid,))
    conn.commit()

def is_admin(uid):
    cur.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    return cur.fetchone() is not None

def get_admins():
    cur.execute("SELECT user_id FROM admins")
    return [a[0] for a in cur.fetchall()]


# ==============================
# COMMANDS
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Welcome to the Anonymous Messaging Bot ✨\nSend your message any time.")


async def handle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    uid = user.id

    add_user(uid, user.username, user.full_name)

    if is_blocked(uid):
        return await update.message.reply_text("⛔ You are blocked.")

    text = update.message.text

    report = f"""
✨ New Message Received ✨
━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {user.full_name}
🔗 Username: @{user.username}
🆔 User ID: {uid}
💬 Message:
{text}
━━━━━━━━━━━━━━━━━━━━━━
"""

    # Send to Owner
    await context.bot.send_message(OWNER_ID, report)

    # Send to Admins
    for admin in get_admins():
        await context.bot.send_message(admin, report)

    await update.message.reply_text("✅ Your message has been delivered.")


async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.message.from_user.id
    if sender != OWNER_ID and not is_admin(sender):
        return

    try:
        _, uid, *msg = update.message.text.split()
        uid = int(uid)
        msg = " ".join(msg)

        fancy = f"""
💬 Reply from Admin/Owner
━━━━━━━━━━━━━━━━━━━━━━
{msg}
━━━━━━━━━━━━━━━━━━━━━━
"""

        await context.bot.send_message(uid, fancy)
        await update.message.reply_text("✨ Fancy reply sent.")
    except:
        await update.message.reply_text("Format: /reply userID message")


async def set_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    try:
        _, uname = update.message.text.split()
        uname = uname.replace("@", "")

        cur.execute("SELECT user_id FROM users WHERE username=?", (uname,))
        r = cur.fetchone()

        if not r:
            return await update.message.reply_text("❌ User not found.")

        add_admin(r[0])
        await update.message.reply_text(f"⭐ @{uname} is now an admin.")
    except:
        await update.message.reply_text("Format: /set @username")


async def unset_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    try:
        _, uname = update.message.text.split()
        uname = uname.replace("@", "")

        cur.execute("SELECT user_id FROM users WHERE username=?", (uname,))
        r = cur.fetchone()

        if not r:
            return await update.message.reply_text("❌ User not found.")

        remove_admin(r[0])
        await update.message.reply_text(f"⚠ @{uname} removed from admins.")
    except:
        await update.message.reply_text("Format: /unset @username")


async def block_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return
    try:
        _, uid = update.message.text.split()
        block_user(int(uid))
        await update.message.reply_text("⛔ User blocked.")
    except:
        await update.message.reply_text("Format: /block userID")


async def unblock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return
    try:
        _, uid = update.message.text.split()
        unblock_user(int(uid))
        await update.message.reply_text("✔ User unblocked.")
    except:
        await update.message.reply_text("Format: /unblock userID")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.message.from_user.id
    if sender != OWNER_ID and not is_admin(sender):
        return

    msg = update.message.text.replace("/broadcast ", "")
    
    fancy = f"""
📢 Broadcast Message
━━━━━━━━━━━━━━━━━━━━━━
{msg}
━━━━━━━━━━━━━━━━━━━━━━
"""

    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()

    for u in users:
        try:
            await context.bot.send_message(u[0], fancy)
        except:
            pass

    await update.message.reply_text("📣 Broadcast sent.")


# ==============================
# MAIN RUNNER
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_cmd))
    app.add_handler(CommandHandler("set", set_admin))
    app.add_handler(CommandHandler("unset", unset_admin))
    app.add_handler(CommandHandler("block", block_cmd))
    app.add_handler(CommandHandler("unblock", unblock_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.User(OWNER_ID)), handle_user))
    app.add_handler(MessageHandler(filters.User(OWNER_ID), reply_cmd))

    app.run_polling()


if __name__ == "__main__":
    main()