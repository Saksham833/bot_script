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
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

# Replace with your actual group ID
GROUP_CHAT_ID = -1002437807718  

# Store user messages for replies
user_message_map = {}

def forward_group_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_message_map[user_id] = update.message.message_id  # Store message ID

    # Forward message to bot admin (You)
    context.bot.send_message(
        chat_id=update.message.chat.id, 
        text=f"🔔 New Message from {update.message.from_user.first_name}: \n\n{update.message.text}"
    )

def reply_to_group(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    original_message_id = user_message_map.get(user_id)

    if original_message_id:
        # Send reply back to the group
        context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"💬 {update.message.text}",
            reply_to_message_id=original_message_id  # Replying to the original message
        )
    else:
        update.message.reply_text("⚠️ No active conversation found.")

def main():
    updater = Updater("7557097031:AAGhadcZUMzxAAmxarFzZi4boeoyUCvem9c", use_context=True)
    dp = updater.dispatcher

    # Listen to messages in the group
    dp.add_handler(MessageHandler(Filters.chat(GROUP_CHAT_ID) & Filters.text, forward_group_message))

    # Listen to replies in bot's private chat
    dp.add_handler(MessageHandler(Filters.private & Filters.text, reply_to_group))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
