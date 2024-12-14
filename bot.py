import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, GEMINI_API_URL, GEMINI_API_KEY  # Import credentials

# Function to query Gemini AI
async def query_gemini_ai(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 300
        }
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("response", "No response received.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error communicating with Gemini AI: {str(e)}"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I’m your Gemini AI-powered coding assistant. Send me a coding task or question!")

# Message handler for user queries
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("Processing your request with Gemini AI...")

    # Get response from Gemini AI
    ai_response = await query_gemini_ai(user_message)
    await update.message.reply_text(f"Here’s the result:\n\n{ai_response}")

# Main function to set up the bot
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
