import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from groq import Groq

# ========== CONFIG ==========
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ========== LOGGING ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== GROQ CLIENT ==========
client = Groq(api_key=GROQ_API_KEY)

# ========== SYSTEM PROMPT ==========
SYSTEM_PROMPT = """You are a smart AI assistant for a Digital Marketing Services business on Telegram.

YOUR JOB:
- Detect the language the user is writing in
- If they write in Urdu or Roman Urdu → reply ONLY in Roman Urdu
- If they write in English → reply ONLY in English
- Be friendly, professional, and helpful

ABOUT THE BUSINESS:
- We offer Digital Marketing Services
- Services: Social Media Marketing, SEO, Content Creation, Paid Ads (Facebook/Google), Telegram Marketing, Brand Building
- We help businesses grow online
- For pricing → tell them to contact directly for custom packages

RULES:
- Always be polite and professional
- Keep replies short (2-4 sentences max)
- If pricing asked → say contact for custom package
- Never give fake information

URDU EXAMPLE:
User: "bhai marketing ki zaroorat hai"
Reply: "Bilkul bhai! Hum aapki digital marketing mein poori madad kar sakte hain. Aapka business kya hai aur kya goal hai? Main best package suggest karunga!"

ENGLISH EXAMPLE:
User: "I need help with social media"
Reply: "Great! We specialize in social media marketing and can help grow your presence. What's your business type and main goal? We'll find the best package for you!"
"""

# ========== AI REPLY ==========
async def get_ai_reply(user_message: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="llama3-8b-8192",
            max_tokens=300,
            temperature=0.7
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return "Sorry, thodi problem hai. Please dobara try karein. 🙏"

# ========== HANDLERS ==========
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
        "Koi bhi sawaal poochein! 😊"
    )
    await update.message.reply_text(welcome_msg)

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_message = update.message.text
    logger.info(f"Message: {user_message}")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await get_ai_reply(user_message)
    await update.message.reply_text(reply)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post or not update.channel_post.text:
        return
    post_text = update.channel_post.text
    prompt = f"Someone posted this on our Digital Marketing channel: '{post_text}'. Write a short engaging comment. Match their language (Urdu or English). Max 2 sentences."
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
    print("🤖 Bot start ho raha hai...")
    print(f"Token exists: {bool(TELEGRAM_BOT_TOKEN)}")
    print(f"Groq key exists: {bool(GROQ_API_KEY)}")

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN nahi mili!")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY nahi mili!")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_private_message))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))

    print("✅ Bot chal raha hai!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
