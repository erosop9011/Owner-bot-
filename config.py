import os

# Super Owner (You)
SUPER_OWNER_ID = 5691270692
SUPER_OWNER_USERNAME = "@incognitovirus"

# Bot Token (Railway environment se auto)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Aesthetic Headers
HEADER = "✨ New Message Received ✨\n━━━━━━━━━━━━━━━━━━━━━━"

# Auto reply to user
AUTO_REPLY = (
    "Your message has been sent to the owner 💌\n"
    "Wait some minutes baby 😘\n"
    "You will receive your reply soon 💕"
)

# Allowed keyword triggers
TRIGGERS = {
    "hi": "Owner will reply soon 💌",
    "hello": "Owner will reply soon 💌",
    "help": "Owner will reply soon 💌",
    "love": "Owner will reply soon 💌"
}
