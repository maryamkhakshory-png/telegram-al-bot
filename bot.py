# bot.py - ربات تلگرام هوش مصنوعی
import asyncio
import aiohttp
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ============================================
# API Key ها رو اینجا وارد کن (فقط همین ۴ تا)
# ============================================

# توکن ربات تلگرام (از @BotFather بگیر)
TELEGRAM_TOKEN = "TOKEN_ROBAT_RO_INJA_BEZAR"

# Gemini API Key (از https://aistudio.google.com/apikey)
GEMINI_API_KEY = "GEMINI_API_KEY_INJA_BEZAR"

# DeepSeek API Key (از https://platform.deepseek.com/api_keys)
DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY_INJA_BEZAR"

# Groq API Key (از https://console.groq.com/keys)
GROQ_API_KEY = "GROQ_API_KEY_INJA_BEZAR"

# ============================================
# بقیه کد رو دست نزن
# ============================================

user_data = {}

class AIChat:
    async def ask_gemini(self, message):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        data = {
            "contents": [{"parts": [{"text": f"به فارسی پاسخ بده: {message}"}]}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                result = await resp.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]

    async def ask_deepseek(self, message):
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "به فارسی پاسخ بده"},
                {"role": "user", "content": message}
            ]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                result = await resp.json()
                return result["choices"][0]["message"]["content"]

    async def ask_groq(self, message):
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "به فارسی پاسخ بده"},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content

    async def ask(self, model, message):
        models = {
            "gemini": self.ask_gemini,
            "deepseek": self.ask_deepseek,
            "groq": self.ask_groq
        }
        try:
            return await models[model](message)
        except Exception as e:
            return f"❌ خطا: {str(e)}"

ai = AIChat()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🤖 ربات هوش مصنوعی چندگانه

🎯 مدل‌ها:
• Gemini 1.5 Flash
• DeepSeek V3  
• Llama 3.1 (Groq)

📌 دستورات:
/model - تغییر مدل
/clear - پاک کردن تاریخچه

💬 پیامت رو بفرست!"""
    await update.message.reply_text(text)

async def model_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Gemini", callback_data="model_gemini")],
        [InlineKeyboardButton("🔍 DeepSeek", callback_data="model_deepseek")],
        [InlineKeyboardButton("🦙 Llama (Groq)", callback_data="model_groq")],
    ]
    user_id = update.effective_user.id
    current = user_data.get(user_id, {}).get("model", "gemini")
    await update.message.reply_text(
        f"مدل فعلی: {current}\nمدل جدید رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def model_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    models = {
        "model_gemini": "gemini",
        "model_deepseek": "deepseek",
        "model_groq": "groq"
    }
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["model"] = models[query.data]
    await query.edit_message_text(f"✅ مدل به {models[query.data]} تغییر کرد!")

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data:
        user_data[user_id]["history"] = []
    await update.message.reply_text("🗑️ تاریخچه پاک شد!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    
    if user_id not in user_data:
        user_data[user_id] = {"model": "gemini", "history": []}
    
    model = user_data[user_id]["model"]
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    response = await ai.ask(model, message)
    
    model_names = {"gemini": "Gemini", "deepseek": "DeepSeek", "groq": "Llama"}
    await update.message.reply_text(f"🤖 [{model_names[model]}]:\n{response}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("model", model_menu))
    app.add_handler(CommandHandler("clear", clear_history))
    app.add_handler(CallbackQueryHandler(model_callback, pattern="^model_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 ربات آماده است!")
    app.run_polling()

if __name__ == "__main__":
    main()
