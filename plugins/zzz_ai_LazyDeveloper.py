import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Client.on_message(filters.private & filters.text)
async def Search(bot, message):
    query   = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    if user_id in ADMINS: return # ignore admins
    await msg.reply_text(
         text=f"<b>ʜᴇʏ {user} 😍 ,\n\nʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ᴍᴏᴠɪᴇs ꜰʀᴏᴍ ʜᴇʀᴇ. ʀᴇǫᴜᴇsᴛ ɪᴛ ɪɴ ᴏᴜʀ <a href=https://t.me/+_AWkWy0499dlZjQ1>Fʀᴇᴇ Mᴏᴠɪᴇ Gʀᴏᴜᴘ</a> ᴏʀ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱʜɪᴘ 👇</b>",   
         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👑 Gᴇᴛ Pʀᴇᴍɪᴜᴍ Mᴇᴍʙᴇʀꜱʜɪᴘ 🫅", url=f"https://t.me/SKadminrobot")]])
    )
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>"
    )
    





















    







        # i am NOT INTRESTED IN BEING YOUR SECOND FATHER... SO DON'T REMOVE MY CREDIT...
        #                               @LazyDeveloperr











        #                                        ...PRESENTING...
        #                          A R T I F i C I A L  -  I N T E L i G E N C E
        #                                      .in  Auto-Filter-Bot.
        #                                         @LazyDeveloperr

                                      










        # this line is for copy-pasters...
        # ...while you are removing my credit and calling yourself a developerr... 
        # _____ just imagine, At that time i am fucking your mom and sis at same time, harder & too harder...





































#
#         i am NOT INTRESTED IN BEING YOUR SECOND FATHER... SO DON'T REMOVE MY CREDIT...
#                                       @LazyDeveloperr
# 
# 
# 
# 
#
#
#
#
#
#
#
#                                                ...PRESENTING...
#                                  A R T I F i C I A L  -  I N T E L i G E N C E
#                                              .in  Auto-Filter-Bot.
#                                                 @LazyDeveloperr
#
#                                       
#
#
#
#
#
#
#
#
#
#
#         this line is for copy-pasters...
#         ...while you are removing my credit and calling yourself a developerr... 
#         _____ just imagine, At that time i am fucking your mom and sis at same time, harder & too harder...
#
