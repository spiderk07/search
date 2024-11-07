import os
import ytthumb
from dotenv import load_dotenv
from utils import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

# Initialize the bot and load environment variables
load_dotenv()

# Your script and bot's client initialization code
@Client.on_message(filters.command("start") & ~filters.channel)
async def start(bot, message):
    await add_user(message.from_user.id, message.from_user.first_name)
    await message.reply(
        text=script.START.format(message.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕', url=f'http://t.me/yourfindbot?startgroup=true')
        ], [InlineKeyboardButton("ʜᴇʟᴘ", callback_data="misc_help"),
            InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data="misc_about")]]))


@Client.on_message(filters.command("help"))
async def help(bot, message):
    await message.reply(text=script.HELP, disable_web_page_preview=True)


@Client.on_message(filters.command("about"))
async def about(bot, message):
    await message.reply(text=script.ABOUT.format((await bot.get_me()).mention),
                        disable_web_page_preview=True)


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
            text += f"Replied Message Forward from Chat ID: `{message.reply_to_message.forward_from_chat.id}\n`"
    await message.reply(text)


@Client.on_callback_query(filters.regex(r"^misc"))
async def misc(bot, update):
    data = update.data.split("_")[-1]
    if data == "home":
        await update.message.edit(text=script.START.format(update.from_user.mention),
                                  disable_web_page_preview=True,
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʜᴇʟᴘ", callback_data="misc_help"),
                                                                     InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data="misc_about")]]))
    elif data == "help":
        await update.message.edit(text=script.HELP,
                                  disable_web_page_preview=True,
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="misc_home")]]))

    elif data == "about":
        await update.message.edit(text=script.ABOUT.format((await bot.get_me()).mention),
                                  disable_web_page_preview=True,
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="misc_home")]]))


BUTTON = [InlineKeyboardButton("🎬 Mᴏᴠɪᴇꜱ Sᴇᴀʀᴄʜ Gʀᴏᴜᴘ🔎", url='https://t.me/+_AWkWy0499dlZjQ1')]


@Client.on_callback_query()
async def cb_data(_, message):
    data = message.data.lower()
    if data == "qualities":
        await message.answer('Select a quality')
        buttons = []
        for quality in ytthumb.qualities():
            buttons.append(
                InlineKeyboardButton(
                    text=ytthumb.qualities()[quality],
                    callback_data=quality
                )
            )
    if data == "back":
        await message.edit_message_reply_markup(photo_buttons)
    if data in ytthumb.qualities():
        thumbnail = ytthumb.thumbnail(
            video=message.message.reply_to_message.text,
            quality=message.data
        )
        await message.answer('Updating')
        await message.edit_message_media(
            media=InputMediaPhoto(media=thumbnail),
            reply_markup=photo_buttons
        )
        await message.answer('Updated Successfully')


@Client.on_message(filters.private & filters.text)
async def send_thumbnail(bot, update):
    message = await update.reply_text(
        text="`Analysing...`",
        disable_web_page_preview=True,
        quote=True
    )
    try:
        if " | " in update.text:
            video = update.text.split(" | ", -1)[0]
            quality = update.text.split(" | ", -1)[1]
        else:
            video = update.text
            quality = "sd"
        thumbnail = ytthumb.thumbnail(
            video=video,
            quality=quality
        )
        await update.reply_photo(
            photo=thumbnail,
            quote=True
        )
        await message.delete()
    except Exception as error:
        await message.edit_text(
            text="<b>ʜᴇʏ {user} 😍 ,\n\nʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ᴍᴏᴠɪᴇꜱ ꜰʀᴏᴍ ʜᴇʀᴇ, ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ <a href=https://t.me/+_AWkWy0499dlZjQ1>Mᴏᴠɪᴇ Sᴇᴀʀᴄʜ Gʀᴏᴜᴘ</a> ᴀɴᴅ ɢᴇᴛ ᴍᴏᴠɪᴇꜱ \n\nआप यहां से फिल्में नहीं प्राप्त कर सकते, आपको मूवी सर्च ग्रुप में ज्वॉइन होना होगा और फिल्में प्राप्त करनी होंगी 👇</b>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([BUTTON])
        )


# New /yt Command to Handle YouTube Link and Quality
@Client.on_message(filters.command("yt") & filters.private & filters.text)
async def yt(bot, message):
    # Extract the text after the command
    input_text = message.text.split(" ", 1)
    
    if len(input_text) < 2:
        await message.reply("Please provide the YouTube link and quality. Example: `/yt https://youtube.com/watch?v=xyz123 sd`")
        return

    # Extract the YouTube link and quality from the message
    youtube_link = input_text[1].split(" | ")[0]
    quality = "sd"  # Default quality
    if " | " in input_text[1]:
        quality = input_text[1].split(" | ")[1]
    
    # Generate the thumbnail using ytthumb
    try:
        thumbnail = ytthumb.thumbnail(video=youtube_link, quality=quality)
        # Send the thumbnail back to the user
        await message.reply_photo(photo=thumbnail, caption=f"Here is the {quality.upper()} quality thumbnail for the video!")
    except Exception as e:
        await message.reply(f"Sorry, I couldn't generate a thumbnail for that video. Error: {str(e)}")
