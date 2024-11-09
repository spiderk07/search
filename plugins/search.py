import asyncio
from info import *
from utils import *
from time import time
from client import User
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

RESULTS_PER_PAGE = 1  # Show one result per page

# Function to delete a message after a delay
async def delete_schedule(bot, message, delay: int):
    await asyncio.sleep(delay)
    try:
        await bot.delete_messages(chat_id=message.chat.id, message_ids=message.id)  # Fixed to use message.id
    except Exception as e:
        print(f"Error occurred while deleting message: {e}")

# Wrapper function to save a message for deletion after a specific time
async def save_dlt_message(bot, message, delete_after_seconds: int):
    await delete_schedule(bot, message, delete_after_seconds)

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
    header = "<b><i>★ Powered by:@Skcreator70</i></b>\n\n🍿 Here are your movie links 👇\n\n"
    footer = "<i>Suggestions: try refining your search if you don't see what you're looking for.</i>"
    page_number = 1  # Default to the first page

    try:
        # List to hold found results
        found_results = []

        # Collect results from channels
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name and name not in found_results:
                    found_results.append(name)

        # Show total result count at the top
        if found_results:
            total_results = len(found_results)
            head = f"{header}🔍 <b>Total Results Found: {total_results}</b>\n\n"
        else:
            # Fallback if no results found
            movies = await search_imdb(query)
            buttons = [[InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")] for movie in movies]
            
            msg = await message.reply_photo(
                photo="https://graph.org/file/1ee45a6e2d4d6a9262a12.jpg",
                caption="<b><i>Sorry, no results found for your query 😕.\nDid you mean any of these?</i></b>", 
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await save_dlt_message(bot, msg, 300)
            return

        # Display the first result (one result per page)
        start_idx = (page_number - 1) * RESULTS_PER_PAGE
        page_result = found_results[start_idx]

        # Create the results message
        results = f"<b><i>🎬 {page_result}</i></b>\n\n{footer}"

        # Set up pagination buttons
        buttons = []
        if page_number > 1:
            buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
        if start_idx + RESULTS_PER_PAGE < total_results:
            buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

        # Send the result message with navigation buttons
        reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
        msg = await message.reply_text(
            text=head + results,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )

        # Schedule deletion of the message after 5 minutes (300 seconds)
        await save_dlt_message(bot, msg, 300)

        # Send a sticker after the movie result
        sticker = "CAACAgIAAxkBAAIrCGUwjom4s9P26nsiP-QAAUV-qDDOhQACcQgAAoSUQUlvaAkaprvOczAE"
        sticker_msg = await message.reply_sticker(sticker)
        
        # Schedule sticker deletion after 5 seconds
        await save_dlt_message(bot, sticker_msg, 5)

    except Exception as e:
        print(f"Error occurred in search function: {e}")
        await message.reply("An error occurred while processing your request. Please try again later.")

@Client.on_callback_query(filters.regex(r"^page"))
async def page_navigation(bot, update):
    try:
        # Extract page number and query from callback data
        data = update.data.split("_")
        page_number = int(data[1])
        query = data[2]

        # Get the list of results from the search
        channels = (await get_group(update.message.chat.id))["channels"]
        found_results = []

        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name and name not in found_results:
                    found_results.append(name)

        # Check if we have results and if we’re on a valid page
        start_idx = (page_number - 1) * RESULTS_PER_PAGE
        if start_idx >= len(found_results):
            await update.answer("No more results available.", show_alert=True)
            return

        # Display the result for the current page
        page_result = found_results[start_idx]
        results = f"<b><i>🎬 {page_result}</i></b>\n\n<i>Suggestions: try refining your search if you don't see what you're looking for.</i>"

        # Display a sticker for 2 seconds before showing the next page
        sticker_id = "CAACAgIAAxkBAAIrCGUwjom4s9P26nsiP-QAAUV-qDDOhQACcQgAAoSUQUlvaAkaprvOczAE"
        sticker_msg = await update.message.reply_sticker(sticker_id)
        await asyncio.sleep(2)
        await sticker_msg.delete()  # Remove the sticker after 2 seconds

        # Update pagination buttons
        buttons = []
        if page_number > 1:
            buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
        if start_idx + RESULTS_PER_PAGE < len(found_results):
            buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

        # Edit the message to show the new page result
        await update.message.edit(
            text=results,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None
        )

        # Schedule deletion of the message after 5 minutes (300 seconds)
        await save_dlt_message(bot, update.message, 300)

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
