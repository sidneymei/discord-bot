import os
import importlib

import discord
from discord import app_commands
from discord.ext import tasks
import aiohttp

from database import Database
from logger import log_err
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
    self.owner_id = int(os.environ.get('OWNER_ID', 0))  # Default to 0 if not set
    self.last_price_state = None  # True if above threshold, False if below

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
    self.price_to_compare = await fetch_comed_price_to_compare(self.price_to_compare_url)
    if self.price_to_compare is None:
      log_err("Failed to fetch ComEd price to compare")

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
          log_err(f"Error: HTTP {response.status}")
      except aiohttp.ClientError as e:
        log_err(f"Error fetching ComEd price: {str(e)}")
    return None

  @tasks.loop(minutes=5)
  async def check_comed_prices(self):
    """
    Periodically check ComEd prices and send alerts if necessary.
    """
    price = await self.get_comed_price()
    if price is not None:
      if self.price_to_compare is None:
        await self.update_price_to_compare()
      if self.price_to_compare is not None:
        current_price_state = price > self.price_to_compare
        if self.last_price_state is None or current_price_state != self.last_price_state:
          await self.send_price_alerts(price)
          self.last_price_state = current_price_state

  async def send_price_alerts(self, price):
    """
    Send price alerts to all subscribed users.

    Args:
      price (float): The current ComEd price.
    """
    subscribed_users = self.db.get_subscribed_users()
    for user_id in subscribed_users:
      await self.send_price_alert(user_id, price)

  async def send_price_alert(self, user_id, price):
    """
    Send a price alert to a specific user.

    Args:
      user_id (int): The Discord user ID to send the alert to.
      price (float): The current ComEd price.
    """
    try:
      user = await self.fetch_user(user_id)
      embed = create_price_embed(price, self.price_to_compare)
      await user.send(embed=embed)
    except discord.errors.Forbidden:
      log_err(f"Unable to send DM to user {user_id}. User might have DMs disabled.")
    except discord.errors.HTTPException as e:
      log_err(f"Error sending DM to user {user_id}: {str(e)}")

  async def on_ready(self):
    """
    Perform actions when the bot is ready and connected to Discord.
    """
    print(f'{self.user} has connected to Discord!')
    await self.set_status()
    # pylint: disable=no-member
    self.check_comed_prices.start()

  async def set_status(self):
    """
    Set the bot's status on Discord.
    """
    await self.change_presence(activity=discord.Activity(
      type=discord.ActivityType.listening, name="/help")
    )

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
        except ImportError as e:
          log_err(f"Failed to load extension {filename[:-3]}: {str(e)}")

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
  log_err(f"Command error for user {interaction.user.id}: {str(error)}")
