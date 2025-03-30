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
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import asyncio

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your new bot token from BotFather
BOT_TOKEN = "8172806018:AAH-ZnBWRiuqWFEG7P7ockuF_f9lwVOAPwk"

# Use in-memory set to track active users during runtime only
active_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command"""
    user_id = update.effective_chat.id
    
    # Add user to active users
    active_users.add(user_id)
    logger.info(f"New user joined: {user_id}")
    
    await update.message.reply_text(
        "👋 Welcome to the Anonymous Message Bot!\n\n"
        "Any message you send here will be forwarded anonymously to everyone else using this bot.\n\n"
        "Note: User list is not stored permanently and will reset when the bot restarts."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forwards messages anonymously to all users"""
    if not update.message or not update.message.text:
        return  # Ignore non-text messages
    
    sender_id = update.effective_chat.id
    message_text = update.message.text
    
    # Skip command-like messages that weren't caught by filters
    if message_text.startswith('/'):
        return
    
    # Make sure sender is in active users list
    active_users.add(sender_id)
    
    # Count forwarded messages
    sent_count = 0
    
    # Forward message to everyone except sender
    users_to_remove = []
    
    for user_id in active_users:
        if user_id != sender_id:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Anonymous: {message_text}"
                )
                sent_count += 1
                await asyncio.sleep(0.05)  # Small delay to avoid rate limits
            except Exception as e:
                logger.warning(f"Failed to send to {user_id}: {e}")
                users_to_remove.append(user_id)
    
    # Remove users who blocked the bot or deleted their account
    for user_id in users_to_remove:
        active_users.discard(user_id)
    
    # Confirm to sender
    if sent_count > 0:
        await update.message.reply_text(
            f"Your message was sent to {sent_count} users."
        )
    else:
        await update.message.reply_text(
            "No users received your message. You're currently the only active user."
        )
    
    logger.info(f"Message forwarded to {sent_count} users")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles errors in the telegram-python-bot library"""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Starts the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot with proper error handling
    try:
        # Clean start with no pending updates
        logger.info("Starting bot...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    except Exception as e:
        logger.critical(f"Critical error starting bot: {e}")

if __name__ == "__main__":
    main()