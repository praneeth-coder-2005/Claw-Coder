from pyrogram import Client, filters
from pyrogram.types import Message
from google.generativeai.models import Code  # Import Code from google.generativeai.models

from config import API_ID, API_HASH, BOT_TOKEN, GOOGLE_API_KEY

# Set your Google API key
Code.api_key = GOOGLE_API_KEY

app = Client("gemini_coder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("code"))
async def generate_code(client: Client, message: Message):
    """Generates code using Gemini."""
    try:
        # Get the user's code request from the message text
        code_request = message.text.replace("/code", "").strip()
        if not code_request:
            await message.reply_text("Please provide a code request after the /code command.")
            return

        # Generate code using Gemini
        response = Code.generate(
            model="gemini-pro-code-bison",  # Use the code generation model
            prompt=code_request
        )
        code_snippet = response.result  # Access the result

        # Send the generated code to the user
        await message.reply_text(f"```\n{code_snippet}\n```", parse_mode="markdown")

    except Exception as e:
        await message.reply_text(f"Error: {e}")

app.run()
