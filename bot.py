import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

from config import TELEGRAM_TOKEN, GEMINI_API_KEY

# Query Gemini AI API with Contextual Awareness
async def query_gemini_ai(prompt: str, context: str = "") -> str:
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
                ],
                "context": context
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

# Message handler for user queries with contextual awareness
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_chat_id = update.message.chat_id
    # Fetch previous context if exists
    context_data = context.user_data.get(str(user_chat_id), "")
    
    # Process user's message with Gemini AI
    await update.message.reply_text("Processing your request with Gemini AI...")
    ai_response = await query_gemini_ai(user_message, context_data)
    
    # Save the context for future use
    context.user_data[str(user_chat_id)] = user_message

    try:
        await update.message.reply_text(ai_response, parse_mode=ParseMode.MARKDOWN_V2)
    except BadRequest as e:
        # Handle BadRequest exception (for example, when the API rejects the message due to special characters)
        await update.message.reply_text(f"Error: {str(e)}. Please try again.")

# Enhanced Inline Keyboard with multiple steps
async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "generate_code":
        context.user_data['step'] = 'code'
        await query.message.reply_text("Enter your code-related question.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="cancel")]]))
    elif data == "cancel":
        await query.message.reply_text("Operation cancelled.", reply_markup=InlineKeyboardMarkup([]))
        del context.user_data['step']
    elif context.user_data.get('step') == 'code':
        ai_response = await query_gemini_ai(query.message.text)
        try:
            await query.message.reply_text(ai_response, parse_mode=ParseMode.MARKDOWN_V2)
        except BadRequest as e:
            await query.message.reply_text(f"Error: {str(e)}. Please try again.")
        del context.user_data['step']
    else:
        await query.message.reply_text("Invalid option. Please try again.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Generate Code", callback_data="generate_code")]]))

# Main function to run the bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_inline_query))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
