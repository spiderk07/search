import asyncio
from info import *
from utils import *
from time import time
from client import User
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

RESULTS_PER_PAGE = 1  # Show one result per page

# Function to save and schedule message deletion
async def save_dlt_message(message, time_to_delete):
    # Here you should save the message and schedule its deletion at the specified time
    # Example implementation (you can modify this as needed):
    await message.delete(time_to_delete)

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
    head = "<b><I>★ Pᴏᴡᴇʀᴇᴅ ʙʏ:@Skcreator7</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n"
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
            buttons = []
            for movie in movies:
                buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])

            # Log and send the photo with IMDb suggestions
            msg = await message.reply_photo(
                photo="https://graph.org/file/1ee45a6e2d4d6a9262a12.jpg",
                caption="<b><i>I couldn't find anything related to your query😕.\nDid you mean any of these?</i></b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            # Display the first result (one result per page)
            start_idx = (page_number - 1) * RESULTS_PER_PAGE
            page_result = found_results[start_idx]

            # Build results for the current page (only the first result)
            results = f"<b><i>♻️ {page_result}</i></b>"

            # Add pagination buttons only
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

        # Save the message for later deletion if necessary
        _time = int(time()) + (15 * 60)  # 15 minutes from now
        await save_dlt_message(msg, _time)

    except Exception as e:
        print(f"Error occurred in search function: {e}")
        await message.reply("An error occurred while processing your request. Please try again later.")


@Client.on_callback_query(filters.regex(r"^page_"))
async def page_navigation(bot, update):
    try:
        # Extract page number and search query from the callback data
        data = update.data.split('_')
        page_number = int(data[1])
        query = data[2]

        # Check if the user is interacting with their own message
        clicked = update.from_user.id
        typed = update.message.reply_to_message.from_user.id
        if clicked != typed:
            return await update.answer("That's not for you! 👀", show_alert=True)

        # Send a sticker response
        sticker = "CAACAgUAAxkBAAEBkV5gY-s6DLph3KDmtY7DsfVwKLRO0wACXwADh5fVAwHEzpoL_qosBA"  # Replace with the sticker you want to send
        await update.message.reply_sticker(sticker)

        # Send a message saying "Searching..💥"
        m = await update.message.edit("Searching..💥")

        # Retrieve the list of channels and perform search
        channels = (await get_group(update.message.chat.id))["channels"]
        found_results = []
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        # Paginate results
        start_idx = (page_number - 1) * RESULTS_PER_PAGE
        end_idx = start_idx + RESULTS_PER_PAGE
        page_results = found_results[start_idx:end_idx]

        # Build results for the current page
        results = "\n\n".join([f"<b><I>♻️ {name}</I></b>" for name in page_results])

        # Build "Next" and "Previous" buttons
        buttons = []
        if page_number > 1:
            buttons.append(InlineKeyboardButton("⏪ Previous", callback_data=f"page_{page_number - 1}_{query}"))
        if end_idx < len(found_results):
            buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

        # Edit the message to display current page results
        await update.message.edit(
            text=f"<u>Search Results 👇\n\nPromoted By </u> <b><I>@GreyMatter_Bots</I></b>\n\n" + results,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([buttons])
        )
    except Exception as e:
        await update.message.edit(f"❌ Error: `{e}`")


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
    movie_info = await search_imdb(imdb_id)

    # Handle cases where movie_info might be a string (e.g., the movie title directly)
    if isinstance(movie_info, dict):
        query = movie_info.get('title', "Unknown Title")
    elif isinstance(movie_info, str):
        query = movie_info  # Assume movie_info itself is the title
    else:
        await update.message.edit("❌ Could not retrieve movie information.")
        return

    # Fetch the channels linked with the group
    channels = (await get_group(update.message.chat.id))["channels"]
    head = "<b><I>★ Pᴏᴡᴇʀᴇᴅ ʙʏ:@Skcreator7</I></b>\n\n🍿 Your Movie Links 👇</I></b>\n\n"
    found_results = []

    try:
        # Search through channels for the movie title
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = msg.text or msg.caption
                if name not in found_results:
                    found_results.append(name)

        # If results are found, display the first result with pagination options if applicable
        if found_results:
            page_number = 1
            start_idx = (page_number - 1) * RESULTS_PER_PAGE
            page_result = found_results[start_idx]

            # Prepare the response with one result and pagination buttons if applicable
            results = f"<b><i>♻️🍿 {page_result}</i></b>"
            buttons = []
            if len(found_results) > RESULTS_PER_PAGE:
                buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page_number + 1}_{query}"))

            await update.message.edit(
                text=head + results,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None
            )

    except Exception as e:
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
    id    = update.data.split("_")[1]
    name  = await search_imdb(id)
    url   = "https://www.imdb.com/title/tt"+id
    text  = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
    await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request Sent To Admin", show_alert=True)
    await update.message.delete(60)
