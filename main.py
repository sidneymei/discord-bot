import asyncio
import os
from bot import bot
from logger import logger

async def main():
  """
  Main coroutine to start the Discord bot.

  This function retrieves the Discord bot token from environment variables,
  starts the bot, and handles specific exceptions that may occur during operation.

  Raises:
    ValueError: If the DISCORD_BOT_TOKEN environment variable is not set.
  """
  token = os.environ.get('DISCORD_BOT_TOKEN')
  
  if not token:
    raise ValueError("No token found. Set the DISCORD_BOT_TOKEN environment variable.")

  try:
    await bot.start(token)
  # pylint: disable=broad-except
  except Exception as e:
    logger.error("An issue occurred during the bot\'s startup: %s", str(e))
  finally:
    await bot.close()

if __name__ == "__main__":
  asyncio.run(main())
