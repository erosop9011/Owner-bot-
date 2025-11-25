import os
import time
import sqlite3
import asyncio
from collections import deque
from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID   = int(os.getenv("OWNER_ID", "0"))

# ===============================
#   DATABASE (SQLite)
# ===============================
db = sqlite3.connect("bot.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS blocked(
    user_id INTEGER PRIMARY KEY
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS admins(
    user_id INTEGER PRIMARY KEY
)""")

db.commit()

def is_admin(uid: int):
    cur.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    return cur.fetchone() is not None

def is_blocked(uid: int):
    cur.execute("SELECT 1 FROM blocked WHERE user_id=?", (uid,))
    return cur.fetchone() is not None

def add_user(uid: int):
    cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (uid,))
    db.commit()

# ===============================
#   QUEUE ENGINE (Stable)
# ===============================
queue = deque()
processing = False

async def queue_push(func, *args, **kwargs):
    queue.append((func, args, kwargs))
    await process_queue()

async def process_queue():
    global processing
    if processing:
        return
    processing = True

    while queue:
        func, args, kwargs = queue.popleft()
        try:
            await func(*args, **kwargs)
        except:
            pass
        await asyncio.sleep(0.03)

    processing = False

# ===============================
#   PANEL
# ===============================
def panel(uid):
    s = str(uid)
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Reply", callback_data=f"reply:{s}"),
            InlineKeyboardButton("✔ Seen",  callback_data=f"seen:{s}")
        ],
        [
            InlineKeyboardButton("❤️", callback_data=f"react_❤️:{s}"),
            InlineKeyboardButton("🔥", callback_data=f"react_🔥:{s}"),
            InlineKeyboardButton("😂", callback_data=f"react_😂:{s}")
        ],
        [
            InlineKeyboardButton("⛔ Block",   callback_data=f"block:{s}"),
            InlineKeyboardButton("🟢 Unblock", callback_data=f"unblock:{s}")
        ],
        [
            InlineKeyboardButton("👑 Admin +", callback_data=f"adminadd:{s}"),
            InlineKeyboardButton("❌ Admin -", callback_data=f"admindel:{s}")
        ]
    ])

# ===============================
#   AI SOFT REPLY
# ===============================
def ai_reply(text: str):
    if not text: return None
    t = text.lower()

    if t in ["hi","hii","hello","hey","hy"]:
        return "🌸 Hey! Your message has been sent to the owner."

    if "thank" in t:
        return "💗 You're welcome! The owner will reply soon."

    if any(w in t for w in ["sad","depress","lonely"]):
        return "🌙 Take care… I’ve sent your message carefully to the owner."

    if any(w in t for w in ["gussa","angry"]):
        return "💫 I’ve forwarded your message. Stay calm 💞"

    return None

# ===============================
#   COUNTRY DETECTION
# ===============================
def detect_country(lang):
    if not lang:
        return "🌎 Unknown region"
    lang = lang.lower()

    if lang.startswith("hi"):
        return "🇮🇳 India"
    if lang.startswith("ur"):
        return "🇵🇰 Pakistan"
    if lang.startswith("bn"):
        return "🇧🇩 Bangladesh"
    if lang.startswith("ne"):
        return "🇳🇵 Nepal"
    return "🌍 Global"

# ===============================
#   TYPING SIMULATION
# ===============================
async def typing_sim(bot, uid):
    await queue_push(bot.send_message, uid, "✍️ Owner is typing…")

# ===============================
#   OWNER REPLY (panel)
# ===============================
reply_waiting = None

async def panel_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global reply_waiting

    q = update.callback_query
    data = q.data
    await q.answer()

    action, uid = data.split(":")
    uid = int(uid)

    bot = context.bot

    if action == "reply":
        reply_waiting = uid
        await q.message.reply_text(f"💬 Type your reply to {uid}:")
        await typing_sim(bot, uid)
        return

    if action == "seen":
        await queue_push(bot.send_message, uid, "💗 Seen by the owner")
        return

    if action.startswith("react_"):
        emo = action.split("_")[1]
        await queue_push(bot.send_message, uid, f"💞 Owner reacted {emo}")
        return

    if action == "block":
        cur.execute("INSERT OR IGNORE INTO blocked(user_id) VALUES(?)",(uid,))
        db.commit()
        await queue_push(bot.send_message, uid, "⛔ You are blocked.")
        return

    if action == "unblock":
        cur.execute("DELETE FROM blocked WHERE user_id=?", (uid,))
        db.commit()
        await queue_push(bot.send_message, uid, "🟢 You are unblocked.")
        return

    if action == "adminadd":
        cur.execute("INSERT OR IGNORE INTO admins(user_id) VALUES(?)",(uid,))
        db.commit()
        await queue_push(bot.send_message, OWNER_ID, f"👑 Admin added: {uid}")
        return

    if action == "admindel":
        cur.execute("DELETE FROM admins WHERE user_id=?", (uid,))
        db.commit()
        await queue_push(bot.send_message, OWNER_ID, f"❌ Admin removed: {uid}")
        return

# ===============================
#   OWNER DIRECT REPLY (panel mode)
# ===============================
async def owner_reply_mode(update, context):
    global reply_waiting
    uid = update.effective_user.id
    if uid != OWNER_ID and not is_admin(uid):
        return

    if reply_waiting is None:
        return

    target = reply_waiting
    reply_waiting = None

    await queue_push(context.bot.send_message, target, update.message.text)
    await update.message.reply_text("✔ Delivered.")

# ===============================
#   OWNER REPLY VIA REPLY-TO
# ===============================
async def reply_to_forward(update, context):
    uid = update.effective_user.id
    if uid != OWNER_ID and not is_admin(uid):
        return

    if not update.message.reply_to_message:
        return

    try:
        txt = update.message.reply_to_message.text
        target = int(txt.split("User ID:")[1].split("\n")[0])
    except:
        return

    await queue_push(context.bot.send_message, target, update.message.text)
    await update.message.reply_text("✔ Delivered (reply-to mode).")

# ===============================
#   USER MESSAGE (TEXT)
# ===============================
last_sent = {}

async def handle_user_text(update, context):
    bot = context.bot
    user = update.effective_user
    uid  = user.id

    if uid == OWNER_ID or is_admin(uid):
        return

    if is_blocked(uid):
        return

    # cooldown
    now = time.time()
    if uid in last_sent and now - last_sent[uid] < 3:
        return
    last_sent[uid] = now

    add_user(uid)

    text = update.message.text

    # AI reply
    auto = ai_reply(text)
    if auto:
        await queue_push(bot.send_message, uid, auto)

    lang = user.language_code
    country = detect_country(lang)

    info = (
        "✨ New Message\n\n"
        f"👤 User ID: {uid}\n"
        f"🌍 {country}\n\n"
        f"💬 {text}"
    )

    await queue_push(bot.send_message, OWNER_ID, info, reply_markup=panel(uid))

    # User acknowledgement
    await queue_push(bot.send_message, uid,
        "🌸 Message delivered.\n💞 The owner will reply soon.\n⏳ Please wait."
    )

# ===============================
#   USER SENDS MEDIA
# ===============================
async def handle_user_media(update, context):
    bot = context.bot
    user = update.effective_user
    uid  = user.id

    if uid == OWNER_ID or is_admin(uid):
        return

    if is_blocked(uid):
        return

    now = time.time()
    if uid in last_sent and now - last_sent[uid] < 3:
        return
    last_sent[uid] = now

    add_user(uid)

    lang = user.language_code
    country = detect_country(lang)

    info = (
        "✨ New Media Message\n\n"
        f"👤 User ID: {uid}\n"
        f"🌍 {country}"
    )

    await queue_push(bot.send_message, OWNER_ID, info, reply_markup=panel(uid))
    await queue_push(update.message.copy, OWNER_ID)

    await queue_push(bot.send_message, uid,
        "🌸 Your media has been delivered.\n💞 The owner will review it soon."
    )

# ===============================
#   BROADCAST
# ===============================
async def broadcast(update, context):
    sender = update.effective_user.id
    if sender != OWNER_ID and not is_admin(sender):
        return

    cur.execute("SELECT user_id FROM users")
    users = [u[0] for u in cur.fetchall()]
    count = 0

    if update.message.reply_to_message:
        media = update.message.reply_to_message

        for uid in users:
            try:
                await queue_push(media.copy, uid)
                count += 1
            except:
                pass

        return await update.message.reply_text(f"📢 Broadcast delivered to {count} users.")

    text = " ".join(context.args)
    if not text:
        return await update.message.reply_text("Use: /broadcast <message>")

    for uid in users:
        try:
            await queue_push(context.bot.send_message, uid, text)
            count += 1
        except:
            pass

    await update.message.reply_text(f"📢 Broadcast sent to {count} users.")

# ===============================
#   START + MAIN
# ===============================
async def start(update, context):
    await update.message.reply_text(
        "🌸 Welcome!\nSend a message and I’ll forward it anonymously to the owner."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # Panel buttons
    app.add_handler(CallbackQueryHandler(panel_buttons))

    # Owner reply systems
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, reply_to_forward))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, owner_reply_mode))

    # Media
    media_filter = (
        filters.PHOTO | filters.VIDEO | filters.AUDIO |
        filters.VOICE | filters.DOCUMENT | filters.ANIMATION
    )
    app.add_handler(MessageHandler(media_filter, handle_user_media))

    # Users text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    print("🔥 UNIQUE ANONYMOUS BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
