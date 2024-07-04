import discord
from discord import app_commands
from discord.ext import tasks
import aiohttp
import os
import importlib
from database import Database
from logger import log_err
from msg import Msg
from dotenv import load_dotenv
from utils import create_price_embed

load_dotenv()

class Bot(discord.Client):
  def __init__(self):
    intents = discord.Intents.default()
    intents.message_content = True
    super().__init__(intents=intents)
    self.tree = app_commands.CommandTree(self)
    self.COMED_API_URL = "https://hourlypricing.comed.com/api?type=currenthouraverage"
    self.PRICE_THRESHOLD = self.get_env_float('PRICE_THRESHOLD')
    self.CHECK_INTERVAL = self.get_env_int('CHECK_INTERVAL')
    self.db = Database('data/bot.db')
    self.owner_id = self.get_env_int('OWNER_ID')
    self.last_price_state = None  # True if above threshold, False if below

  def get_env(self, key):
    value = os.getenv(key)
    if value is None:
      raise ValueError(f"Environment variable {key} is not set")
    return value

  def get_env_int(self, key):
    return int(self.get_env(key))

  def get_env_float(self, key):
    return float(self.get_env(key))

  async def setup_hook(self):
    await self.load_commands()
    await self.tree.sync()

  async def load_commands(self):
    for filename in os.listdir('commands'):
      if filename.endswith('.py') and not filename.startswith('__'):
        try:
          module_name = f'commands.{filename[:-3]}'
          module = importlib.import_module(module_name)
          importlib.reload(module)
          if hasattr(module, 'setup') and callable(module.setup):
            module.setup(self)
        except Exception as e:
          log_err(f"Failed to load extension {filename[:-3]}: {str(e)}")

  async def get_comed_price(self):
    async with aiohttp.ClientSession() as session:
      try:
        async with session.get(self.COMED_API_URL) as response:
          if response.status == 200:
            data = await response.json()
            if data:
              return float(data[0]['price'])
          log_err(f"Error: HTTP {response.status}")
      except Exception as e:
        log_err(f"Error fetching ComEd price: {str(e)}")
    return None

  async def on_ready(self):
    print(f'{self.user} has connected to Discord!')
    await self.set_status()
    self.check_comed_prices.change_interval(minutes=self.CHECK_INTERVAL)
    self.check_comed_prices.start()

  async def set_status(self):
    await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))

  @tasks.loop()
  async def check_comed_prices(self):
    price = await self.get_comed_price()
    if price is not None:
      current_price_state = price > self.PRICE_THRESHOLD
      if self.last_price_state is None or current_price_state != self.last_price_state:
        await self.send_price_alerts(price)
        self.last_price_state = current_price_state

  async def send_price_alerts(self, price):
    subscribed_users = self.db.get_subscribed_users()
    for user_id in subscribed_users:
      await self.send_price_alert(user_id, price)

  async def send_price_alert(self, user_id, price):
    try:
      user = await self.fetch_user(user_id)
      embed = create_price_embed(price, self.PRICE_THRESHOLD)
      await user.send(embed=embed)
    except discord.errors.Forbidden:
      log_err(f"Unable to send DM to user {user_id}. User might have DMs disabled.")
    except Exception as e:
      log_err(f"Error sending DM to user {user_id}: {str(e)}")

bot = Bot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
  if isinstance(error, app_commands.errors.CheckFailure):
    await interaction.response.send_message(Msg.PERM_ERR, ephemeral=True)
  else:
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)
  log_err(f"Command error for user {interaction.user.id}: {str(error)}")