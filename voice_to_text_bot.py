import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import speech_recognition as sr
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert voice message to text"""
    try:
        await update.message.chat.send_action("typing")
        
        # Get the voice message file
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        voice_data = await voice_file.download_as_bytearray()
        audio_file = BytesIO(voice_data)
        
        # Transcribe using speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio)
            await update.message.reply_text(f"📝 {text}")
        except sr.UnknownValueError:
            await update.message.reply_text("❌ Could not understand the audio. Try again please.")
        except sr.RequestError:
            await update.message.reply_text("❌ Speech service error.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ An error occurred.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Send me a voice message and I'll convert it to text!")

def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable not set")
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
