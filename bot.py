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

# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
# import logging

# # Enable logging
# logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Replace with your actual bot token
# BOT_TOKEN = "7557097031:AAEoOZYnnc-kr0k8Y12g8q81h4EyHQZgvK0"

# # Store user chat IDs
# user_chat_ids = set()  

# async def start(update: Update, context: CallbackContext) -> None:
#     """Handles the /start command"""
#     chat_id = update.message.chat_id
#     user_chat_ids.add(chat_id)  # Store user ID

#     await update.message.reply_text("👋 Welcome! Send a message, and I'll forward it anonymously to everyone.")

# async def forward_message(update: Update, context: CallbackContext) -> None:
#     """Sends the received message to all users anonymously"""
#     user_chat_ids.add(update.message.chat_id)  # Store sender in list
#     message_text = update.message.text

#     # Broadcast message to all stored users
#     for chat_id in user_chat_ids:
#         if chat_id != update.message.chat_id:  # Avoid sending the message back to the sender
#             try:
#                 await context.bot.send_message(chat_id=chat_id, text=f"{message_text}")
#             except Exception as e:
#                 logger.warning(f"Failed to send message to {chat_id}: {e}")

# async def admin_broadcast(update: Update, context: CallbackContext) -> None:
#     """Allows admin (you) to send a message to all users"""
#     admin_id = update.message.chat_id
#     message_text = update.message.text

#     # Ensure admin is in the user list
#     user_chat_ids.add(admin_id)

#     # Broadcast message
#     for chat_id in user_chat_ids:
#         try:
#             await context.bot.send_message(chat_id=chat_id, text=f"📢 Admin Message: {message_text}")
#         except Exception as e:
#             logger.warning(f"Failed to send message to {chat_id}: {e}")

# def main():
#     """Main function to run the bot"""
#     app = Application.builder().token(BOT_TOKEN).build()

#     # Start command
#     app.add_handler(CommandHandler("start", start))

#     # Handle user messages
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

#     # Allow admin to broadcast messages
#     app.add_handler(MessageHandler(filters.TEXT & filters.User("YOUR_ADMIN_USER_ID"), admin_broadcast))

#     print("🤖 Bot is running...")
#     logger.info("Bot started successfully")

#     app.run_polling(drop_pending_updates=True, timeout=60)

# if __name__ == "__main__":
#     main()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import os

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
BOT_TOKEN = "7557097031:AAExyCWJTmM8BLlhnMLm6qq-hJQaSlP_8sw"

# Store user chat IDs - use a file for persistence
USER_DATA_FILE = "user_chat_ids.txt"

# Load existing user IDs from file
def load_user_ids():
    user_chat_ids = set()
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                for line in f:
                    try:
                        user_chat_ids.add(int(line.strip()))
                    except ValueError:
                        continue
        except Exception as e:
            logger.error(f"Error loading user IDs: {e}")
    return user_chat_ids

# Save user IDs to file
def save_user_ids(user_chat_ids):
    try:
        with open(USER_DATA_FILE, 'w') as f:
            for chat_id in user_chat_ids:
                f.write(f"{chat_id}\n")
    except Exception as e:
        logger.error(f"Error saving user IDs: {e}")

# Initialize user IDs
user_chat_ids = load_user_ids()

async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command"""
    chat_id = update.effective_chat.id
    user_chat_ids.add(chat_id)  # Store user ID
    save_user_ids(user_chat_ids)  # Save to file

    await update.message.reply_text("👋 Welcome! Send a message, and I'll forward it anonymously to everyone.")
    logger.info(f"New user joined: {chat_id}. Total users: {len(user_chat_ids)}")

async def forward_message(update: Update, context: CallbackContext) -> None:
    """Sends the received message to all users anonymously"""
    sender_id = update.effective_chat.id
    user_chat_ids.add(sender_id)  # Make sure sender is in the list
    save_user_ids(user_chat_ids)  # Save to file
    
    message_text = update.message.text
    
    # Log activity but protect privacy
    logger.info(f"Message received from {sender_id} to forward to {len(user_chat_ids)-1} users")

    # Broadcast message to all stored users
    for chat_id in user_chat_ids:
        if chat_id != sender_id:  # Avoid sending the message back to the sender
            try:
                await context.bot.send_message(chat_id=chat_id, text=f"Anonymous: {message_text}")
            except Exception as e:
                logger.warning(f"Failed to send message to {chat_id}: {e}")
                # If user blocked the bot or deleted their account, consider removing them
                if "blocked" in str(e).lower() or "chat not found" in str(e).lower():
                    user_chat_ids.discard(chat_id)
                    save_user_ids(user_chat_ids)
                    logger.info(f"Removed user {chat_id} due to: {e}")

async def stats(update: Update, context: CallbackContext) -> None:
    """Provide stats about the number of users"""
    await update.message.reply_text(f"📊 Current number of users: {len(user_chat_ids)}")

def main():
    """Main function to run the bot"""
    # Always use drop_pending_updates=True to avoid the conflict error
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    # Handle user messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    # Set proper polling parameters to avoid conflicts
    print("🤖 Bot is running...")
    logger.info(f"Bot started successfully with {len(user_chat_ids)} users loaded")

    # The key fix for the conflict error is setting drop_pending_updates=True
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()