import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✅ Bot အလုပ်လုပ်နေပါပြီ!\n\n"
        "🎙️ အသံဖိုင် (Voice Message) သို့မဟုတ် 📝 စာတိုများ ပို့ပေးပါ။ "
        "အလိုအလျောက် မြန်မာဘာသာ သို့မဟုတ် အင်္ဂလိပ်ဘာသာသို့ ပြန်ဆိုပေးပါမည်။"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    await update.message.reply_text("🔄 ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပါ...")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Translate the following text to Myanmar language if it's English, or to English if it's Myanmar:\n\n{user_text}"
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားအယွင်းရှိပါသည်: {str(e)}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🎙️ အသံဖိုင်ကို လက်ခံရရှိပါသည်။ ဘာသာပြန်နေပါပြီ...")
    
    try:
        # Download voice file
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        file_path = "voice_input.ogg"
        await voice_file.download_to_drive(file_path)

        # Upload and process audio with Gemini
        uploaded_audio = client.files.upload(file=file_path)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                uploaded_audio,
                "Listen to this audio. Transcribe it and translate it into Burmese (Myanmar language). Also provide the original transcription."
            ]
        )
        
        await update.message.reply_text(response.text)

        # Cleanup local audio file
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ အသံ ဘာသာပြန်ရာတွင် အမှားအယွင်းရှိပါသည်: {str(e)}")

def main() -> None:
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN မရှိပါ။ .env ဖိုင်ကို စစ်ဆေးပါ။")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("🤖 Bot စတင်ပွဲထုတ်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
