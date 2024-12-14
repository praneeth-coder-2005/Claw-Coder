import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, GEMINI_API_KEY  # Import credentials

# Query Gemini AI API
async def query_gemini_ai(prompt: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY  # Your API Key
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        # Send POST request to the Gemini AI API
        response = requests.post(url, headers=headers, params=params, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            # Extract generated content
            return result.get("content", "No content received from Gemini AI.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini AI: {str(e)}"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I’m your Gemini AI-powered coding assistant. Send me a question or coding task, and I'll help!"
    )

# Message handler for user queries
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("Processing your request with Gemini AI...")

    # Get response from Gemini AI
    ai_response = await query_gemini_ai(user_message)
    await update.message.reply_text(f"Here’s the result:\n\n{ai_response}")

# Main function to run the bot
def main():
    # Initialize the application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
