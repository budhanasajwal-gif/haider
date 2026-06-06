import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from groq import Groq

# ========== CONFIGURATION ==========
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ========== LOGGING ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== GROQ CLIENT ==========
client = Groq(api_key=GROQ_API_KEY)

# ========== SYSTEM PROMPT ==========
SYSTEM_PROMPT = """You are a smart AI assistant for a Digital Marketing Services business on Telegram (channel: @sajawalbudhana5).

YOUR JOB:
- Detect the language the user is writing in
- If they write in Urdu or Roman Urdu → reply ONLY in Roman Urdu (easy to read)
- If they write in English → reply ONLY in English
- Be friendly, professional, and helpful

ABOUT THE BUSINESS:
- We offer Digital Marketing Services
- Services: Social Media Marketing, SEO, Content Creation, Paid Ads (Facebook/Google), Telegram Marketing, Brand Building
- We help businesses grow online
- For pricing → tell them to contact directly

RULES:
- Always be polite and professional
- Keep replies short (2-4 sentences max)
- If pricing asked → say "Apni requirements batao, main custom package suggest karunga"
- If interested → ask for their business type and goals
- Never give fake info

URDU EXAMPLE:
User: "bhai marketing ki zaroorat hai"
Reply: "Bilkul bhai! Hum aapki digital marketing mein poori madad kar sakte hain 🚀 Aapka business kya hai aur kya goal hai? Main best package suggest karunga!"

ENGLISH EXAMPLE:
User: "I need help with social media"
Reply: "Great! We specialize in social media marketing and can help grow your presence 🚀 What's your business type and main goal? We'll find the best package for you!"
"""

# ========== AI REPLY FUNCTION ==========
async def get_ai_reply(user_message: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="llama3-8b-8192",  # Free model on Groq
            max_tokens=300,
            temperature=0.7
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "Sorry, thodi problem hai. Please dobara try karein ya directly contact karein. 🙏"

# ========== HANDLERS ==========

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "Bhai"
    welcome_msg = (
        f"👋 Assalam o Alaikum {user_name}!\n\n"
        "Welcome to our Digital Marketing Services! 🚀\n\n"
        "Hum in services mein help karte hain:\n"
        "📱 Social Media Marketing\n"
        "🔍 SEO & Content Creation\n"
        "💰 Paid Ads (Facebook/Google)\n"
        "📢 Telegram Marketing\n"
        "🏷️ Brand Building\n\n"
        "Koi bhi sawaal poochein, main yahan hoon! 😊\n"
        "Ask me anything, I'm here to help!"
    )
    await update.message.reply_text(welcome_msg)

# Private DM handler
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_message = update.message.text
    user = update.effective_user
    logger.info(f"DM from {user.first_name} (@{user.username}): {user_message}")

    # Typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    reply = await get_ai_reply(user_message)
    await update.message.reply_text(reply)

# Channel post handler
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post or not update.channel_post.text:
        return

    post_text = update.channel_post.text
    logger.info(f"Channel post detected: {post_text[:50]}")

    prompt = (
        f"Someone posted this on our Digital Marketing channel: '{post_text}'\n"
        "Write a short engaging comment to boost engagement. "
        "Match their language (Urdu or English). Keep it under 2 sentences."
    )

    reply = await get_ai_reply(prompt)

    try:
        await context.bot.send_message(
            chat_id=update.channel_post.chat_id,
            text=reply,
            reply_to_message_id=update.channel_post.message_id
        )
    except Exception as e:
        logger.error(f"Channel reply error: {e}")

# ========== MAIN ==========
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable nahi mili!")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable nahi mili!")

    print("🤖 Bot start ho raha hai...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_private_message))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))

    print("✅ Bot chal raha hai! Rokne ke liye Ctrl+C dabao.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
