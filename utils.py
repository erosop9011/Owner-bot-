import asyncio
from telegram.constants import ChatAction

async def typing_effect(bot, chat_id, duration=1.0):
    """Show typing animation safely."""
    await bot.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(duration)

def format_report(header, user, message_text):
    """Message format for owner/admins."""
    return (
        f"{header}\n"
        f"Name: {user.full_name}\n"
        f"Username: @{user.username}\n"
        f"User ID: {user.id}\n"
        f"Message:\n{message_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
  )
