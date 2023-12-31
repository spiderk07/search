import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Bot.on_message(filters.incoming)
async def inline_handlers(_, event: Message):
    if event.text == '/start':
        return
    answers = f'**Aᴅᴍɪɴ ➠ @SKadminrobot \n\n**'
    async for message in User.search_messages(chat_id=Config.CHANNEL_ID, limit=1, query=event.text):
        if message.text:
            thumb = None
            f_text = message.text
            msg_text = message.text.html
            if "|||" in message.text:
                f_text = message.text.split("|||", 1)[0]
                msg_text = message.text.html.split("|||", 1)[0]
            answers += f'**🎬 ' + '' + f_text.split("\n", 1)[0] + '' + '\n ➠ ' + '' + f_text.split("\n", 2)[-1] + ' \n**'
    try:
        msg = await event.reply_text(answers)
        await asyncio.sleep(300)
        await event.delete()
        await msg.delete()
    except Exception as e:
        print(f"[{Config.BOT_SESSION_NAME}] - Failed to Answer - {event.from_user.first_name}")

