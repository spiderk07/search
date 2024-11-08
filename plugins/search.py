import asyncio
from info import *
from utils import *
from time import time
from client import User
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

RESULTS_PER_PAGE = 1  # Show one result per page

async def delete_schedule(bot, message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Error occurred while deleting message: {e}")

async def save_dlt_message(bot, message, delete_time: int):
    await delete_schedule(bot, message, delete_time)

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    f_sub = await force_sub(bot, message)
    if not f_sub:
        return

    channels = (await get_group(message.chat.id))["channels"]
    if not channels or message.text.startswith("/"):
        return

    query = message.text
    head = "<b><I>★ Powered by:@Skcreator70</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n"
    page_number = 1

    try:
        found_results = []
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        if not found_results:
            movies = await search_imdb(query)
            buttons = [[InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")] for movie in movies]
            msg = await message.reply_photo(
                photo="https://graph.org/file/1ee45a6e2d4d6a9262a12.jpg",
                caption="<b><i>No results found for your query. Did you mean one of these?</i></b>", 
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            start_idx = (page_number - 1) * RESULTS_PER_PAGE
            page_result = found_results[start_idx]
            results = f"<b><i>🎬 {page_result}</i></b>"
            
            buttons = []
            if page_number > 1:
                buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
            if start_idx + RESULTS_PER_PAGE < len(found_results):
                buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

            reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
            msg = await message.reply_text(
                text=head + results,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
            _time = int(time()) + (5 * 60)
            await save_dlt_message(bot, msg, _time)

        # Send the sticker after sending movie results or suggestions
        sticker = "CAACAgIAAxkBAAEBHZJkGRgMPLKkz7qHvO2S7A2prh4gAAL5wADg6_9zQKaB1l3SO6f4d0E"
        await message.reply_sticker(sticker)

    except Exception as e:
        print(f"Error in search function: {e}")
        await message.reply("An error occurred. Please try again later.")

@Client.on_callback_query(filters.regex(r"^page"))
async def page_navigation(bot, update):
    try:
        data = update.data.split("_")
        page_number = int(data[1])
        query = data[2]

        channels = (await get_group(update.message.chat.id))["channels"]
        found_results = []

        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        start_idx = (page_number - 1) * RESULTS_PER_PAGE
        page_result = found_results[start_idx]
        results = f"<b><i>🎬 {page_result}</i></b>"

        buttons = []
        if page_number > 1:
            buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
        if start_idx + RESULTS_PER_PAGE < len(found_results):
            buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

        await update.message.edit(
            text=results,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None
        )

        # Send a sticker after each result page
        sticker = "CAACAgIAAxkBAAEBHZJkGRgMPLKkz7qHvO2S7A2prh4gAAL5wADg6_9zQKaB1l3SO6f4d0E"
        await update.message.reply_sticker(sticker)

    except Exception as e:
        print(f"Error during pagination: {e}")
        await update.answer("An error occurred. Please try again.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    try:      
        clicked = update.from_user.id
        typed = update.message.reply_to_message.from_user.id if update.message.reply_to_message else None
        if clicked != typed:
            return await update.answer("That's not for you! 👀", show_alert=True)

        await update.message.edit("Searching... 💥")

        imdb_id = update.data.split("_")[-1]
        movie_info = await search_imdb(imdb_id)
        query = movie_info.get('title') if isinstance(movie_info, dict) else movie_info

        channels = (await get_group(update.message.chat.id))["channels"]
        head = "<b><I>★ Powered by:@Skcreator70</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n"
        found_results = []

        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        if found_results:
            page_number = 1
            start_idx = (page_number - 1) * RESULTS_PER_PAGE
            page_result = found_results[start_idx]
            results = f"<b><i>🎬 {page_result}</i></b>"

            buttons = []
            if page_number > 1:
                buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
            if start_idx + RESULTS_PER_PAGE < len(found_results):
                buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

            await update.message.edit(
                text=head + results,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None
            )

            await asyncio.sleep(300)
            await update.message.delete()

        else:
            msg = await update.message.edit(
                "No results found! You may request this movie from the group admin.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🎯 Request To Admin 🎯", callback_data=f"request_{imdb_id}")]]
                )
            )
            await asyncio.sleep(300)
            await msg.delete()

    except Exception as e:
        print(f"Error during recheck: {e}")
        await update.message.edit(f"❌ Error: `{e}`")

@Client.on_callback_query(filters.regex(r"^request"))
async def request(bot, update):
    try:
        clicked = update.from_user.id
        typed = update.message.reply_to_message.from_user.id if update.message.reply_to_message else None
        if clicked != typed:
            return await update.answer("That's not for you! 👀", show_alert=True)

        admin = (await get_group(update.message.chat.id))["user_id"]
        id = update.data.split("_")[1]
        name = await search_imdb(id)
        url = f"https://www.imdb.com/title/tt{id}"
        text = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
        await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
        await update.answer("✅ Request Sent To Admin", show_alert=True)
        await update.message.delete(60)
