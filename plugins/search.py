import asyncio
from info import *
from utils import *
from time import time
from client import User
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

RESULTS_PER_PAGE = 1  # Show one result per page

# Define the delete_schedule function to delete a message after a delay
async def delete_schedule(bot, message, delay: int):
    await asyncio.sleep(delay)
    try:
        # Use bot parameter to delete the message
        await message.delete()
    except Exception as e:
        print(f"Error occurred while deleting message: {e}")

# Function to save a scheduled message for deletion
async def save_dlt_message(bot, message, delete_time: int):
    # Pass bot parameter along with the message and time to delete
    await delete_schedule(bot, message, delete_time)

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
    head = "<b><I>★ Powered by:@Skcreator70</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n"
    page_number = 1  # Default to the first page

    try:
        # List to hold found results
        found_results = []

        # Collect results from channels
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        # If no results are found, search IMDb and send suggestions
        if not found_results:
            movies = await search_imdb(query)
            buttons = [[InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")] for movie in movies]
            
            # Send a message with IMDb suggestions
            msg = await message.reply_photo(
                photo="https://graph.org/file/1ee45a6e2d4d6a9262a12.jpg",
                caption="<b><i>I couldn't find anything related to your query😕.\nDid you mean any of these?</i></b>", 
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            # Display the first result (one result per page)
            start_idx = (page_number - 1) * RESULTS_PER_PAGE
            page_result = found_results[start_idx]
            
            # Build the results for the current page (only one result)
            results = f"<b><i>🎬 {page_result}</i></b>"
            
            # Add pagination buttons only if there are more results
            buttons = []
            if page_number > 1:
                buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
            if start_idx + RESULTS_PER_PAGE < len(found_results):
                buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))
            
            # Log and send the message with results and pagination buttons
            reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
            msg = await message.reply_text(
                text=head + results,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )

            # Automatically delete message after 300 seconds (5 minutes)
            _time = int(time()) + (5 * 60)
            await save_dlt_message(bot, msg, _time)

        # Send a sticker after the movie result
        sticker = "CAACAgIAAxkBAAIrCGUwjom4s9P26nsiP-QAAUV-qDDOhQACcQgAAoSUQUlvaAkaprvOczAE"  # Replace with your sticker ID
        await message.reply_sticker(sticker)

    except Exception as e:
        print(f"Error occurred in search function: {e}")
        await message.reply("An error occurred while processing your request. Please try again later.")

@Client.on_callback_query(filters.regex(r"^page"))
async def page_navigation(bot, update):
    try:
        # Extract page number and query from callback data
        data = update.data.split("_")
        page_number = int(data[1])  # Extract the page number
        query = data[2]  # Extract the original query

        # Get the list of results from the search
        channels = (await get_group(update.message.chat.id))["channels"]
        found_results = []

        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        # Show the results for the current page
        start_idx = (page_number - 1) * RESULTS_PER_PAGE
        if start_idx >= len(found_results):
            await update.answer("No more results available.", show_alert=True)
            return

        page_result = found_results[start_idx]
        results = f"<b><i>🎬 {page_result}</i></b>"

        # Display the sticker for 2 seconds before updating to the next page
        sticker_id = "CAACAgIAAxkBAAIrCGUwjom4s9P26nsiP-QAAUV-qDDOhQACcQgAAoSUQUlvaAkaprvOczAE"  # Replace with your sticker ID
        sticker_msg = await update.message.reply_sticker(sticker_id)
        await asyncio.sleep(2)
        await sticker_msg.delete()  # Remove the sticker after 2 seconds

        # Create navigation buttons
        buttons = []
        if page_number > 1:
            buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
        if start_idx + RESULTS_PER_PAGE < len(found_results):
            buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

        # Edit the message with the results and pagination buttons
        await update.message.edit(
            text=results,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None
        )

    except Exception as e:
        print(f"Error occurred during pagination: {e}")
        await update.answer("An error occurred while processing your request. Please try again later.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    clicked = update.from_user.id
    try:      
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete()       
    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)

    await update.message.edit("Searching... 💥")

    # Extract the IMDb movie ID from the callback data
    imdb_id = update.data.split("_")[-1]
    
    # Search for movie information using the IMDb ID
    try:
        movie_info = await search_imdb(imdb_id)

        # Handle cases where movie_info might be a string (e.g., the movie title directly)
        query = movie_info.get('title') if isinstance(movie_info, dict) else movie_info

        # Fetch the channels linked with the group
        channels = (await get_group(update.message.chat.id))["channels"]
        head = "<b><I>★ Powered by:@Skcreator70</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n"
        found_results = []

        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        if found_results:
            # Display the first result (one result per page)
            page_number = 1
            start_idx = (page_number - 1) * RESULTS_PER_PAGE
            page_result = found_results[start_idx]

            # Build the results for the current page (only one result)
            results = f"<b><i>🎬 {page_result}</i></b>"

            # Add pagination buttons only if there are more results
            buttons = []
            if page_number > 1:
                buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
            if start_idx + RESULTS_PER_PAGE < len(found_results):
                buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

            # Edit the message with results and pagination buttons
            await update.message.edit(
                text=head + results,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None
            )

            # Automatically delete message after 600 seconds
            await asyncio.sleep(300)
            await update.message.delete()

        else:
            # If no results are found, send an option to request the movie from an admin
            msg = await update.message.edit(
                "Still no results found! You may request this movie from the group admin.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request from Admin 🎯", url="https://t.me/SKadminrobot")]])
            )

            # Automatically delete the message after 600 seconds (10 minutes)
            await save_dlt_message(bot, msg, int(time()) + (10 * 60))

    except Exception as e:
        print(f"Error occurred during recheck: {e}")
        await update.answer("An error occurred while processing your request. Please try again later.", show_alert=True)
