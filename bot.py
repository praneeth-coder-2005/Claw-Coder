import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import TELEGRAM_TOKEN, GEMINI_API_URL, GEMINI_API_KEY  # Import credentials

# Query Gemini AI for coding assistance
def query_gemini_ai(prompt: str) -> str:
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

# Define the /start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! I’m your Gemini AI-powered coding assistant. Send me a coding task or question!")

# Define the message handler
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    update.message.reply_text("Processing your request with Gemini AI...")
    
    # Get response from Gemini AI
    ai_response = query_gemini_ai(user_message)
    update.message.reply_text(f"Here’s the result:\n\n{ai_response}")

# Main function to initialize the bot
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
