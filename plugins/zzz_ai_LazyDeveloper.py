import asyncio
from client import User
from pyrogram import Client, filters 
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Client.on_message(filters.private & filters.text)
async def lazy_answer(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    if user_id in ADMINS: return # ignore admins
    await message.reply_text(
         text=f"<b>ʜᴇʏ {user} 😍 ,\n\nʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ᴍᴏᴠɪᴇs ꜰʀᴏᴍ ʜᴇʀᴇ. ʀᴇǫᴜᴇsᴛ ɪᴛ ɪɴ ᴏᴜʀ <a href=https://t.me/+_AWkWy0499dlZjQ1>Fʀᴇᴇ Mᴏᴠɪᴇ Gʀᴏᴜᴘ</a> ᴏʀ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱʜɪᴘ 👇</b>",   
         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👑 Gᴇᴛ Pʀᴇᴍɪᴜᴍ Mᴇᴍʙᴇʀꜱʜɪᴘ 🫅", url=f"https://t.me/SKadminrobot")]])
    )
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>"
    )
