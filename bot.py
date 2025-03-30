from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import asyncio
from datetime import datetime

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your new bot token from BotFather
BOT_TOKEN = "7557097031:AAGhadcZUMzxAAmxarFzZi4boeoyUCvem9c"

# Use in-memory sets to track users
active_users = set()
suspended_users = set()

# Dictionary to track message delivery stats
message_stats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command"""
    user_id = update.effective_chat.id
    
    # Add user to active users
    active_users.add(user_id)
    logger.info(f"New user joined: {user_id}")
    
    await update.message.reply_text(
        "👋 Welcome to the Anonymous Message Bot!\n\n"
        "Any message you send here will be forwarded anonymously to other users.\n\n"
        "Use /user to see how many people received your message."
    )

async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /user command"""
    user_id = update.effective_chat.id
    
    if user_id in message_stats:
        last_message = message_stats[user_id]
        await update.message.reply_text(
            f"Your last message was sent to {last_message['recipient_count']} users at {last_message['timestamp']}."
        )
    else:
        await update.message.reply_text(
            "You haven't sent any messages yet."
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
    
    # Reactivate suspended users if possible
    users_to_reactivate = []
    for user_id in suspended_users:
        try:
            await context.bot.send_chat_action(chat_id=user_id, action="typing")
            users_to_reactivate.append(user_id)
        except:
            pass  # User is still unreachable
    
    # Move reactivated users back to active list
    for user_id in users_to_reactivate:
        suspended_users.remove(user_id)
        active_users.add(user_id)
    
    # Count forwarded messages
    sent_count = 0
    users_to_remove = []
    
    for user_id in active_users:
        if user_id != sender_id:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f" {message_text}"
                )
                sent_count += 1
                await asyncio.sleep(0.05)  # Small delay to avoid rate limits
            except Exception as e:
                logger.warning(f"Failed to send to {user_id}: {e}")
                users_to_remove.append(user_id)
    
    # Move failed users to suspended instead of removing them
    for user_id in users_to_remove:
        active_users.discard(user_id)
        suspended_users.add(user_id)
    
    # Store message stats for the /user command
    message_stats[sender_id] = {
        'recipient_count': sent_count,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    logger.info(f"Message forwarded to {sent_count} users")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles errors in the telegram-python-bot library"""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Starts the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("user", user_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot with proper error handling
    try:
        logger.info("Starting bot...")
        application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Critical error starting bot: {e}")

if __name__ == "__main__":
    main()