from utils import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import requests
from io import BytesIO

# Replace with the actual admin user ID
ADMIN_USER_ID = 5928972764

YOUTUBE_URL_PATTERN = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"

def get_hd_thumbnail_url(video_id):
    """Returns the highest resolution YouTube thumbnail URL."""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def get_fallback_thumbnail_url(video_id):
    """Returns a fallback YouTube thumbnail URL (lower resolution)."""
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

@Client.on_message(filters.user(ADMIN_USER_ID) & filters.regex(YOUTUBE_URL_PATTERN))
async def send_thumbnail_from_link(bot, message):
    match = re.search(YOUTUBE_URL_PATTERN, message.text)
    if match:
        video_id = match.group(1)
        
        # Attempt to get the highest resolution thumbnail
        thumbnail_url = get_hd_thumbnail_url(video_id)
        response = requests.get(thumbnail_url)

        # If HD thumbnail is not available, fallback to a lower resolution
        if response.status_code != 200:
            thumbnail_url = get_fallback_thumbnail_url(video_id)
            response = requests.get(thumbnail_url)

        if response.status_code == 200:
            # Send the image as a file
            image = BytesIO(response.content)
            image.name = f"{video_id}_thumbnail.jpg"
            await bot.send_photo(message.chat.id, image, caption="Here is the YouTube thumbnail in HD quality!")
        else:
            await message.reply_text("Couldn't download the thumbnail. Please check the video link.")

@Client.on_message(filters.command("start") & ~filters.channel)
async def start(bot, message):
    await add_user(message.from_user.id, message.from_user.first_name)
    await message.reply(
        text=script.START.format(message.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕', url=f'http://t.me/Movieslinks_robot?startgroup=true')],
            [InlineKeyboardButton("ʜᴇʟᴘ", callback_data="misc_help"), InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data="misc_about")]
        ])
    )

@Client.on_message(filters.command("help"))
async def help(bot, message):
    await message.reply(text=script.HELP, disable_web_page_preview=True)

@Client.on_message(filters.command("about"))
async def about(bot, message):
    await message.reply(text=script.ABOUT.format((await bot.get_me()).mention), disable_web_page_preview=True)

@Client.on_message(filters.command("stats"))
async def stats(bot, message):
    g_count, g_list = await get_groups()
    u_count, u_list = await get_users()
    await message.reply(script.STATS.format(u_count, g_count))

@Client.on_message(filters.command("id"))
async def id(bot, message):
    text = f"Current Chat ID: `{message.chat.id}`\n"
    if message.from_user:
        text += f"Your ID: `{message.from_user.id}`\n"
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            text += f"Replied User ID: `{message.reply_to_message.from_user.id}`\n"
        if message.reply_to_message.forward_from:
            text += f"Replied Message Forward from User ID: `{message.reply_to_message.forward_from.id}`\n"
        if message.reply_to_message.forward_from_chat:
            text += f"Replied Message Forward from Chat ID: `{message.reply_to_message.forward_from_chat.id}`\n"
    await message.reply(text)

@Client.on_message(filters.private & ~filters.user(ADMIN_USER_ID))
async def auto_reply_private(bot, message):
    await message.reply_text("Hello! Thank you for your message. The admin will respond shortly.")

@Client.on_callback_query(filters.regex(r"^misc"))
async def misc(bot, update):
    data = update.data.split("_")[-1]
    if data == "home":
        await update.message.edit(
            text=script.START.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʜᴇʟᴘ", callback_data="misc_help"), InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data="misc_about")]
            ])
        )
    elif data == "help":
        await update.message.edit(
            text=script.HELP,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="misc_home")]])
        )
    elif data == "about":
        await update.message.edit(
            text=script.ABOUT.format((await bot.get_me()).mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="misc_home")]])
        )
