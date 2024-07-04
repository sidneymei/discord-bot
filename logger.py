import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
  logger = logging.getLogger('bot')
  logger.setLevel(logging.INFO)

  # Ensure the data directory exists
  os.makedirs('data', exist_ok=True)

  handler = RotatingFileHandler('data/bot.log', maxBytes=1000000, backupCount=5)
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)

  logger.addHandler(handler)

  return logger

logger = setup_logger()

def log_cmd(user_id, cmd_name):
  logger.info(f"User {user_id} used command: {cmd_name}")

def log_err(err_msg):
  logger.error(f"Error: {err_msg}")