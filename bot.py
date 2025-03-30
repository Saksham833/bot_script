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

# Replace with your bot token
BOT_TOKEN = "7557097031:AAGhadcZUMzxAAmxarFzZi4boeoyUCvem9c"

# Replace with your actual group ID
GROUP_CHAT_ID = -1002437807718 

# Store user messages for replies
user_message_map = {}

async def start(update: Update, context: CallbackContext) -> None:
    """Start command for bot."""
    await update.message.reply_text("Send me a message, and I'll post it anonymously in the group.")

async def forward_group_message(update: Update, context: CallbackContext) -> None:
    """Forwards a message from a user to the group."""
    user_id = update.message.from_user.id
    message_id = update.message.message_id
    user_message_map[user_id] = message_id  # Store message ID

    # Forward message to group
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"Anonymous: {update.message.text}"
    )

async def reply_to_group(update: Update, context: CallbackContext) -> None:
    """Replies to the original message in the group."""
    user_id = update.message.chat_id
    original_message_id = user_message_map.get(user_id)

    if original_message_id:
        # Send reply back to the group
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"💬 {update.message.text}",
            reply_to_message_id=original_message_id  # Replying to the original message
        )
    else:
        await update.message.reply_text("⚠️ No active conversation found.")

def main():
    """Main function to run the bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Command to start the bot
    app.add_handler(CommandHandler("start", start))

    # Listen to messages in the group and forward them
    app.add_handler(MessageHandler(filters.Chat(GROUP_CHAT_ID) & filters.TEXT, forward_group_message))

    # Listen to replies in bot's private chat
    app.add_handler(MessageHandler(filters.Private & filters.TEXT, reply_to_group))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
