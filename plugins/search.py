import asyncio
from info import *
from utils import *
from time import time
from client import User
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

RESULTS_PER_PAGE = 1  # Show one result per page

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    f_sub = await force_sub(bot, message)
    if not f_sub:
        return
    channels = (await get_group(message.chat.id))["channels"]
    if not channels:
        return
    if message.text.startswith("/"):
        return

    query = message.text
    head = "<b><I>★ Powered by:@Skcreator7</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n"
    page_number = 1  # Default to the first page

    try:
        found_results = []
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        if not found_results:
            # No results found in channels; suggest IMDb movies
            movies = await search_imdb(query)
            buttons = [[InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")] for movie in movies]

            msg = await message.reply_photo(
                photo="https://graph.org/file/1ee45a6e2d4d6a9262a12.jpg",
                caption="<b><i>I couldn't find anything related to your query😕.\nDid you mean any of these?</i></b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            # Display the first page of results
            start_idx = (page_number - 1) * RESULTS_PER_PAGE
            page_result = found_results[start_idx]
            results = f"<b><i>♻️ {page_result}</i></b>"

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

        # Schedule deletion of the message after 600 seconds (10 minutes)
        await schedule_deletion(msg, 600)

    except Exception as e:
        print(f"Error occurred in search function: {e}")
        await message.reply("An error occurred while processing your request. Please try again later.")

async def schedule_deletion(msg, delay):
    """Schedule deletion of a message after a given delay in seconds."""
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception as e:
        print(f"Error occurred while deleting message: {e}")

@Client.on_callback_query(filters.regex(r"^page_"))
async def page_navigation(bot, update):
    try:
        print("Callback data received:", update.data)  # Debugging

        # Extracting data from callback
        data = update.data.split('_')
        page_number = int(data[1])
        query = data[2]

        # Check if the user interacting is the message sender
        clicked = update.from_user.id
        typed = update.message.reply_to_message.from_user.id
        if clicked != typed:
            return await update.answer("That's not for you! 👀", show_alert=True)

        # Send a sticker to simulate loading
        await update.message.reply_sticker("CAACAgUAAxkBAAEBkV5gY-s6DLph3KDmtY7DsfVwKLRO0wACXwADh5fVAwHEzpoL_qosBA")

        # Wait briefly to let the sticker display before updating the results
        await asyncio.sleep(1.5)  # Adjust delay as needed for best effect

        # Search across channels
        channels = (await get_group(update.message.chat.id))["channels"]
        found_results = []
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        # Calculate result range for the page
        start_idx = (page_number - 1) * RESULTS_PER_PAGE
        end_idx = start_idx + RESULTS_PER_PAGE
        page_results = found_results[start_idx:end_idx]

        # Check if there are results
        if not page_results:
            await update.answer("No more results to show.", show_alert=True)
            return

        # Format results and setup buttons
        results = "\n\n".join([f"<b><I>♻️ {name}</I></b>" for name in page_results])
        buttons = []
        if page_number > 1:
            buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
        if end_idx < len(found_results):
            buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

        # Update the message with new results and navigation buttons
        await update.message.edit(
            text=f"<b><I>★ Powered by:@Skcreator7</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n" + results,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([buttons])
        )

        # Schedule deletion
        await schedule_deletion(update.message, 600)

    except Exception as e:
        print(f"Error in page_navigation: {e}")
        await update.message.edit(f"❌ Error: `{e}`")

@Client.on_callback_query(filters.regex(r"^recheck_"))
async def imdb_recheck(bot, update):
    try:
        # Extracting IMDb movie ID from callback data
        movie_id = update.data.split("_")[1]
        print(f"Rechecking IMDb for movie ID: {movie_id}")  # Debugging

        # Fetching movie details
        movie = await search_imdb(movie_id)
        if not movie:
            return await update.answer("No details found for this movie.", show_alert=True)

        # Formatting and sending movie details
        url = f"https://www.imdb.com/title/tt{movie_id}"
        text = f"<b>IMDb Title:</b> {movie['title']}\n\n" + \
               f"<b>Description:</b> {movie.get('description', 'No description available.')}\n\n" + \
               f"<a href='{url}'>More on IMDb</a>"

        await update.message.edit(text, disable_web_page_preview=True)

    except Exception as e:
        print(f"Error in imdb_recheck: {e}")
        await update.message.edit(f"❌ Error: `{e}`")

                
@Client.on_callback_query(filters.regex(r"^request"))
async def request(bot, update):
    clicked = update.from_user.id
    try:
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete()
    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)

    admin = (await get_group(update.message.chat.id))["user_id"]
    id = update.data.split("_")[1]
    name = await search_imdb(id)
    url = "https://www.imdb.com/title/tt" + id
    text = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
    await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request Sent To Admin", show_alert=True)
    await update.message.delete(60)
