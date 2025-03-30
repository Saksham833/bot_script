from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

# Replace with your actual bot token
BOT_TOKEN = "7557097031:AAGhadcZUMzxAAmxarFzZi4boeoyUCvem9c"

# Replace with your actual group chat ID
GROUP_CHAT_ID = -1002437807718  

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Send me a message, and I'll post it anonymously in the group.")

async def forward_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    if user_message:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Anonymous: {user_message}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
