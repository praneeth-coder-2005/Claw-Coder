import re
import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, Context import TELEGRAM_TOKEN, GEMINI_API_KEY

# Query Gemini AI API with error handling and special characters escaped
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
        response = requests.post(url, headers=headers, params=params, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            candidates = result.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                # Escaping special characters individually
                content = re.sub(r'([{}_*\\\[\]()#+\-\.!])', r'\\\1', content)
                return content[:4096]  # Truncate response to 4096 characters
            else:
                return "No candidates found."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini AI: {str(e)}"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Ask me anything, and I'll assist with Gemini AI.")

# Handle messages with large code responses split into multiple messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("Processing your request...")
    ai_response = await query_gemini_ai(user_message)

    # Improved message splitting for large responses
    parts = [ai_response[i:i+4096] for i in range(0, len(ai_response), 4096)]
    for part in parts:
        await update.message.reply_text(part, parse_mode="MarkdownV2")

# Main function to run the bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
