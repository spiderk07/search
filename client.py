# client.py

from info import *  # Importing API details from info.py
from pyrogram import Client
from subprocess import Popen

# Initialize User Client with session string
try:
    User = Client(name="user", session_string=SESSION)
except Exception as e:
    raise ValueError("Failed to initialize the User client with SESSION. Please check your session string.") from e

# Initialize Bot Client with API ID, API Hash, and Bot Token
DlBot = Client(name="auto-delete", 
               api_id=API_ID,
               api_hash=API_HASH,           
               bot_token=BOT_TOKEN)

class Bot(Client):   
    def __init__(self):
        super().__init__(   
            "bot",
            api_id=API_ID,
            api_hash=API_HASH,           
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"}  # Load plugins from the plugins folder
        )
    
    async def start(self):                        
        await super().start()
        
        try:
            await User.start()  # Start User client with session string
        except Exception as e:
            raise RuntimeError("Failed to start User client. Verify your session string and API credentials.") from e
        
        # Start the delete script as a subprocess
        Popen("python3 -m utils.delete", shell=True)
        print("Bot Started 🔧 Powered By @TechnicalCynite")   
    
    async def stop(self, *args):
        # Ensure the User client is stopped as well
        await User.stop()
        await super().stop()
        print("Bot Stopped")
