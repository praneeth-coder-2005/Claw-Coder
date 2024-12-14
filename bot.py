import requests
import json
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN, GEMINI_API_KEY

# Query Gemini AI API
async def query_gemini_ai(prompt: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
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
            candidates = result.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                # Escape problematic characters
                content = re.sub(r'(?<!\\)[().{}\-]', r'\\\g<0>', content)  # Escaping problematic characters
                return content
            else:
                return "No candidates found in the response from Gemini AI."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini AI: {str(e)}"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I’m your Gemini AI-powered assistant. Send me a question or task, and I'll help!"
    )

# Message handler for user queries
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("Processing your request with Gemini AI...")

    # Get response from Gemini AI
    ai_response = await query_gemini_ai(user_message)

    # Send the AI response with MarkdownV2 parsing
    await update.message.reply_text(ai_response, parse_mode="MarkdownV2")

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
