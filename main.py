import os
import logging
import httpx
import datetime
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, CallbackContext)

# 🔥 Load API Keys from Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set in environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Set in environment

# 🚀 Choose Groq Model (LLaMA 3 or Mixtral)
GROQ_MODEL = "llama3-8b-8192"  # Change to "llama3-70b-8192" or "mixtral-8x7b-32768" if needed

# 🚀 Knowledge Base (Custom Replies)
bot_knowledge = {
    "Emmanuel": "Emmanuel is the CEO, Founder, and Developer of BASE! 🚀 BASE to the moon!",
    "CEO": "Emmanuel is the CEO of BASE! 🚀",
    "Founder": "Emmanuel is the Founder of BASE!",
    "DEV": "Emmanuel is the Developer of BASE! 💻",
    "MOD": "Wisdow is the MOD keeping things in order!",
    "Project": "BASE is the future! 🚀 Stay bullish!"
}

# 🚀 Function to Generate AI Responses with Word Limit
async def chat_with_groq(user_message, chat_history=[]):
    user_message_lower = user_message.lower().strip()

    # Quick Replies for Simple Messages
    if user_message_lower in ["hello", "hi", "hey"]:
        return "How are you doing? How's your day going? 😊"
    if "what is today" in user_message_lower or "today's date" in user_message_lower:
        return f"Today's date is {datetime.datetime.now().strftime('%A, %B %d, %Y')} 📅"
    if "what time is it" in user_message_lower or "current time" in user_message_lower:
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')} ⏰"

    # Check Knowledge Base
    for key, value in bot_knowledge.items():
        if key.lower() in user_message_lower:
            return value

    # AI Chat Generation
    system_prompt = """
    You are a friendly and engaging Web3 mod in a Telegram group.
    - Keep responses short (max 30 words).
    - Remove 'Hey there!'.
    - Use at least one emoji in every response.
    - Encourage users to reply back.
    - Hype BASE whenever mentioned!
    """

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": user_message}],
        "temperature": 0.7,
        "max_tokens": 150  # Limit response length
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        words = ai_response.split()
        if len(words) > 30:
            ai_response = " ".join(words[:30]) + "..."
        return ai_response
    else:
        return "I couldn't process that request right now. Try again!"

# 🚀 Start Command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("🔥 Welcome to BASE! 🚀\n\nGlad to have you here! How's your day going? 😊")

# 🚀 Handle Messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    if update.message.from_user.is_bot:
        return

    chat_history = []
    if update.message.reply_to_message:
        chat_history.append({"role": "assistant", "content": update.message.reply_to_message.text})

    if f"@{context.bot.username}" in user_text or update.message.chat.type == "private" or update.message.reply_to_message:
        try:
            ai_response = await chat_with_groq(user_text, chat_history)
            await update.message.reply_text(ai_response)
        except Exception as e:
            print(f"Error: {e}")
            await update.message.reply_text("Couldn't process that. Try again!")

# 🚀 Main Function to Run Bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
