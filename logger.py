import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
  """
  Set up and configure the logger for the bot.

  Returns:
    logging.Logger: Configured logger object.
  """
  bot_logger = logging.getLogger('bot')
  bot_logger.setLevel(logging.INFO)

  # Ensure the data directory exists
  os.makedirs('data', exist_ok=True)

  handler = RotatingFileHandler('data/bot.log', maxBytes=1000000, backupCount=5)
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)

  bot_logger.addHandler(handler)

  return bot_logger

logger = setup_logger()
