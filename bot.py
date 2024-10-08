import os
import importlib

import discord
from discord import app_commands
from discord.ext import tasks
import aiohttp

from database import Database
from logger import logger
from msg import Msg
from utils import create_price_embed, fetch_comed_price_to_compare

class Bot(discord.Client):
  """
  Main Bot class that inherits from discord.Client.
  Handles price checks, alerts, and command loading.
  """

  def __init__(self):
    """
    Initialize the Bot with necessary attributes and settings.
    """
    intents = discord.Intents.default()
    intents.message_content = True
    super().__init__(intents=intents)

    self.tree = app_commands.CommandTree(self)
    self.comed_api_url = "https://hourlypricing.comed.com/api?type=currenthouraverage"
    self.price_to_compare_url = "https://plugin.illinois.gov/understanding-the-price-to-compare/price-to-compare-comed.html"
    self.price_to_compare = None
    self.db = Database('data/bot.db')
    self.last_price = None

  async def setup_hook(self):
    """
    Perform setup tasks when the bot starts.
    """
    await self.load_commands()
    await self.tree.sync()
    await self.update_price_to_compare()

  async def update_price_to_compare(self):
    """
    Update the price to compare from the ComEd website.
    """
    price = await fetch_comed_price_to_compare(self.price_to_compare_url)
    if price is None:
      if self.price_to_compare is None:
        self.price_to_compare = 6.9
        logger.error("Failed to fetch comparison price; defaulting to 6.9")
      else:
        logger.error("Failed to fetch comparison price; keeping previous value of %s", self.price_to_compare)
    else:
      self.price_to_compare = price
      logger.info("Updated comparison price to %s", self.price_to_compare)

  async def get_comed_price(self):
    """
    Fetch the current ComEd price from the API.

    Returns:
      float or None: The current price if successful, None otherwise.
    """
    async with aiohttp.ClientSession() as session:
      try:
        async with session.get(self.comed_api_url) as response:
          if response.status == 200:
            data = await response.json()
            if data:
              return float(data[0]['price'])
          logger.error("Error: HTTP %s", response.status)
      except aiohttp.ClientError as e:
        logger.error("Error fetching ComEd price %s", str(e))
    return None

  @tasks.loop(minutes=5)
  async def send_price_alerts(self):
    """
    Periodically check ComEd prices and send alerts if necessary.
    """
    current_price = await self.get_comed_price()
    if current_price is not None and current_price == self.last_price:
      return

    subscribed_users = self.db.get_subscribed_users()
    for user_id, threshold in subscribed_users:
      user_threshold = threshold if threshold is not None else self.price_to_compare
      if user_threshold is not None and (
        (self.last_price is None) or
        (self.last_price <= user_threshold < current_price) or
        (self.last_price > user_threshold >= current_price)
      ):
        await self.send_price_alert(user_id, current_price, user_threshold)

    self.last_price = current_price

  @tasks.loop(hours=168) # 168 hours = 1 week
  async def update_price_to_compare_weekly(self):
    """
    Update the price to compare on a weekly basis.
    """
    await self.update_price_to_compare()

  async def send_price_alert(self, user_id, price, threshold):
    """
    Send a price alert to a specific user.

    Args:
      user_id (int): The Discord user ID to send the alert to.
      price (float): The current ComEd price.
    """
    try:
      user = await self.fetch_user(user_id)
      embed = create_price_embed(price, threshold)
      await user.send(embed=embed)
    except discord.errors.Forbidden:
      logger.error("Unable to send DM to user %s. User might have DMs disabled.", user_id)
    except discord.errors.HTTPException as e:
      logger.error("Error sending DM to user %s: %s", user_id, str(e))

  async def on_ready(self):
    """
    Perform actions when the bot is ready and connected to Discord.
    """
    logger.info('Bot has successfully connected as %s.', {self.user.name})
    # pylint: disable=no-member
    self.send_price_alerts.start()
    self.update_price_to_compare_weekly.start()

  async def load_commands(self):
    """
    Load all command modules from the 'commands' directory.
    """
    for filename in os.listdir('commands'):
      if filename.endswith('.py') and not filename.startswith('__'):
        try:
          module_name = f'commands.{filename[:-3]}'
          module = importlib.import_module(module_name)
          importlib.reload(module)
          if hasattr(module, 'setup') and callable(module.setup):
            module.setup(self)
          logger.info('The "%s" command has been loaded successfully', module_name)
        except ImportError as e:
          logger.error("Failed to load extension %s: %s", filename[:-3], str(e))

bot = Bot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
  """
  Handle errors that occur during command execution.

  Args:
    interaction (discord.Interaction): The interaction that caused the error.
    error (app_commands.AppCommandError): The error that occurred.
  """
  if isinstance(error, app_commands.errors.CheckFailure):
    await interaction.response.send_message(Msg.PERM_ERR, ephemeral=True)
  else:
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)
  logger.error("Command error for user %s: %s", interaction.user.id, str(error))
