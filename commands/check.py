import time
import discord
from discord import app_commands
from logger import logger
from msg import Msg
from utils import create_price_embed

class CheckCooldown:
  """
  A class to manage cooldown for the check command.
  """

  def __init__(self, rate, per):
    """
    Initialize the CheckCooldown object.

    Args:
      rate (int): Number of uses allowed
      per (int): Time period in seconds
    """
    self.rate = rate
    self.per = per
    self.last_check = {}

  def is_on_cooldown(self, user_id):
    """
    Check if the command is on cooldown for a user.

    Args:
      user_id (int): The ID of the user to check

    Returns:
      bool: True if on cooldown, False otherwise
    """
    current_time = time.time()
    if user_id in self.last_check:
      elapsed = current_time - self.last_check[user_id]
      return elapsed < self.per
    return False

  def update_cooldown(self, user_id):
    """
    Update the last check time for a user.

    Args:
      user_id (int): The ID of the user to update
    """
    self.last_check[user_id] = time.time()

cooldown = CheckCooldown(rate=1, per=60)  # 1 use per 60 seconds

@app_commands.command(name="check", description=Msg.CMD_DESC_CHECK)
async def check(interaction: discord.Interaction):
  """
  Check the current ComEd electricity price.

  This command retrieves the current ComEd price and sends it to the user.
  It has a cooldown of 60 seconds per user.

  Args:
    interaction (discord.Interaction): The interaction object representing the command invocation.
  """
  user_id = interaction.user.id

  if cooldown.is_on_cooldown(user_id):
    await interaction.response.send_message(Msg.CHECK_COOLDOWN, ephemeral=True)
    return

  try:
    current_price = await interaction.client.get_comed_price()

    if current_price is not None:
      embed = create_price_embed(current_price, interaction.client.price_to_compare)
      await interaction.response.send_message(embed=embed, ephemeral=True)
      cooldown.update_cooldown(user_id)
      logger.info('User %s used the "check" command.', user_id)
    else:
      await interaction.response.send_message(Msg.COMED_PRICE_ERR, ephemeral=True)
  # pylint: disable=broad-except
  except Exception as e:
    logger.error('The "check" command failed for user %s: %s', user_id, str(e))
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)

def setup(bot):
  """
  Add the check command to the bot's command tree.

  Args:
    bot: The bot instance to add the command to.
  """
  bot.tree.add_command(check)
