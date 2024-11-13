from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

class Script:
    START = """**Hello {} 🤟**
   
I am **Movies Link Search Bot**. I am the best Channel Link Search Bot! 
I will filter your channel posts automatically and send them in your group chat when someone searches for it."""

    HELP = """To Use me In A Group:

- Add me to your group & channel with all permissions. 
- Send /verify in group & wait for approval, or directly contact the owner after the request at @SKadminrobot.
- After verification, send /connect YourChannelID
  Example: /connect -100xxxxxxxxxx
- Done ✅. <b><I>Enjoy 💜❤</I></b>

To remove a channel, use: /disconnect-100xxxxxxxxxxx.
This will help you to remove an indexed channel from your group.

Get connected channels list with: /connections"""

    ABOUT = """Developed By @SkFilmBox

✯ Join: <a href='https://t.me/Sk_films_box'>Backup Channel</a>
✯ Join: <a href='https://t.me/Skcreator70'>Diskwala Links</a>
✯ Movies: <a href='https://t.me/+_AWkWy0499dlZjQ1'>Search Group</a>
✯ WhatsApp: <a href='https://whatsapp.com/channel/0029Va69Ts2C6ZvmEWsHNo3c'>Movie Channel</a>
✯ Bot Server: <a href='https://heroku.com'>Heroku</a>"""

    STATS = """My Status 💫

👥 Users: {}
🧿 Groups: {}"""

    BROADCAST = """<u>{}</u>

Total: `{}`
Remaining: `{}`
Success: `{}`
Failed: `{}`"""

# Command handler for /start that sends both a welcome message and a photo
def start(update: Update, context: CallbackContext):
    # Get the user's first name for personalization
    user_first_name = update.effective_user.first_name
    welcome_message = Script.START.format(user_first_name)
    
    # First, send the welcome text message
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_message,
        parse_mode='Markdown'
    )

    # URL or path of the photo to send (update with a real image URL or local path)
    photo_url = "https://graph.org/file/410116023ab0cdc93f120-e5252eead8f3b4ccac.jpg"  # Replace with an actual image URL or file path

    # Then, send the photo with an optional caption
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption="Welcome to the Movies Link Search Bot! 🎬",
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Script.HELP,
        parse_mode='HTML'
    )

def about_command(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Script.ABOUT,
        parse_mode='HTML'
    )

def stats_command(update: Update, context: CallbackContext):
    # Example values, replace with actual logic to get user and group counts
    user_count = 100
    group_count = 20
    stats_message = Script.STATS.format(user_count, group_count)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=stats_message,
        parse_mode='Markdown'
    )

# Main function to set up the bot and command handlers
def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("about", about_command))
    dp.add_handler(CommandHandler("stats", stats_command))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
