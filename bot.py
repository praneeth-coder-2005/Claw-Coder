import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
                # If the message contains code, format it nicely and return it with a copy button
                if "```" in content:
                    return content, True  # Return the code and flag for showing the copy button
                else:
                    return content, False
            else:
                return "No candidates found in the response.", False
        else:
            return f"Error: {response.status_code} - {response.text}", False
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini AI: {str(e)}", False

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
    ai_response, show_copy_button = await query_gemini_ai(user_message)

    # If response contains code, show copy button
    if show_copy_button:
        await update.message.reply_text(
            f"Here’s the result:\n\n{ai_response}", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Copy", callback_data=f"copy:{ai_response}")]
            ])
        )
    else:
        await update.message.reply_text(f"Here’s the result:\n\n{ai_response}")

# Callback handler for the copy button
async def copy_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(":")
    
    if data[0] == "copy":
        code_to_copy = data[1]
        await query.answer("Code copied!")
        await query.edit_message_text(f"Code copied!\n\n{code_to_copy}")

# Main function to run the bot
def main():
    # Initialize the application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(copy_code))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
