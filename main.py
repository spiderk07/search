from client import Bot
from plugins.misc import download_youtube_thumbnail
from pyrogram import Client, filters

# Replace with the actual admin user ID
ADMIN_USER_ID = 5928972764

@Client.on_message(filters.command("thumbnail") & filters.user(ADMIN_USER_ID))
async def send_thumbnail(client, message):
    try:
        # Extract video ID from the command text
        video_id = message.text.split(" ", 1)[1]
        thumbnail_path = download_youtube_thumbnail(video_id)
        
        if thumbnail_path:
            await client.send_photo(message.chat.id, thumbnail_path, caption="Here is the YouTube thumbnail!")
        else:
            await message.reply_text("Couldn't download the thumbnail. Please check the video ID.")
    except IndexError:
        await message.reply_text("Please provide a valid YouTube video ID.")

@Client.on_message(filters.private & ~filters.user(ADMIN_USER_ID))
async def auto_reply_private(client, message):
    await message.reply_text("Hello! Thank you for your message. The admin will respond shortly.")

print("Bot Started 👍")
Bot().run()
