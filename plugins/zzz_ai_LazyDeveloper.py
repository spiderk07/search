from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace with your token obtained from BotFather
TOKEN = '6922466504:AAFSCMMHX4N2nmagHqwpCLWb0bsJXpsB4Xg'

# Replace with your admin user IDs
ADMINS = [5928972764, 7891356780]

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.first_name
    user_id = update.message.from_user.id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hey {user}, you can't get movies from here. Please request it in our Free Movie Group or get premium membership.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Get Premium Membership", url="https://t.me/SKadminrobot")]])
    )
    context.bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"#PM_MSG\n\nName: {user}\n\nID: {user_id}\n\nMessage: {update.message.text}"
    )

def echo(update: Update, context: CallbackContext) -> None:
    if update.message.text.startswith("/") or update.message.text.startswith("#"):
        return  # ignore commands and hashtags

    user_id = update.message.from_user.id
    if user_id in ADMINS:
        return  # ignore admins

    start(update, context)

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
