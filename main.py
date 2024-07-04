import asyncio
import os
from dotenv import load_dotenv
from bot import bot

load_dotenv()

async def main():
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        raise ValueError("No token found. Set the DISCORD_BOT_TOKEN environment variable.")
    
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())