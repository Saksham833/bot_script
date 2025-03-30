# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
# import asyncio

# # Replace with your actual bot token
# BOT_TOKEN = "7557097031:AAGhadcZUMzxAAmxarFzZi4boeoyUCvem9c"

# # Replace with your actual group chat ID
# GROUP_CHAT_ID = -1002437807718  

# async def start(update: Update, context: CallbackContext) -> None:
#     await update.message.reply_text("Send me a message, and I'll post it anonymously in the group.")

# async def forward_message(update: Update, context: CallbackContext) -> None:
#     user_message = update.message.text
#     if user_message:
#         await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Anonymous: {user_message}")

# def main():
#     app = Application.builder().token(BOT_TOKEN).build()
    
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

#     print("Bot is running...")
#     app.run_polling()

# if __name__ == "__main__":
#     main()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
BOT_TOKEN = "7557097031:AAExyCWJTmM8BLlhnMLm6qq-hJQaSlP_8sw"

# Store user chat IDs
user_chat_ids = set()  

async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command"""
    chat_id = update.message.chat_id
    user_chat_ids.add(chat_id)  # Store user ID

    await update.message.reply_text("👋 Welcome! Send a message, and I'll forward it anonymously to everyone.")

async def forward_message(update: Update, context: CallbackContext) -> None:
    """Sends the received message to all users anonymously"""
    user_chat_ids.add(update.message.chat_id)  # Store sender in list
    message_text = update.message.text

    # Broadcast message to all stored users
    for chat_id in user_chat_ids:
        if chat_id != update.message.chat_id:  # Avoid sending the message back to the sender
            try:
                await context.bot.send_message(chat_id=chat_id, text=f"{message_text}")
            except Exception as e:
                logger.warning(f"Failed to send message to {chat_id}: {e}")

async def admin_broadcast(update: Update, context: CallbackContext) -> None:
    """Allows admin (you) to send a message to all users"""
    admin_id = update.message.chat_id
    message_text = update.message.text

    # Ensure admin is in the user list
    user_chat_ids.add(admin_id)

    # Broadcast message
    for chat_id in user_chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"📢 Admin Message: {message_text}")
        except Exception as e:
            logger.warning(f"Failed to send message to {chat_id}: {e}")

def main():
    """Main function to run the bot"""
    app = Application.builder().token(BOT_TOKEN).build()

    # Start command
    app.add_handler(CommandHandler("start", start))

    # Handle user messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    # Allow admin to broadcast messages
    app.add_handler(MessageHandler(filters.TEXT & filters.User("YOUR_ADMIN_USER_ID"), admin_broadcast))

    print("🤖 Bot is running...")
    logger.info("Bot started successfully")

    app.run_polling(drop_pending_updates=True, timeout=60)

if __name__ == "__main__":
    main()
