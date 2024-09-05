import discord
from discord import app_commands
from logger import logger
from msg import Msg

@app_commands.command(name="toggle", description=Msg.CMD_DESC_TOGGLE)
@app_commands.describe(threshold="The price threshold for alerts.")
async def toggle(interaction: discord.Interaction, threshold: float = None):
  """
  Toggle the price alert subscription for a user.

  This command allows users to subscribe or unsubscribe from price alerts.
  Users can optionally set a price threshold for their alerts.

  Args:
    interaction (discord.Interaction): The interaction object representing the command invocation.
    threshold (float, optional): The price threshold for alerts. Defaults to None.
  """
  user_id = interaction.user.id

  try:
    subscribed_user = interaction.client.db.get_subscribed_user(user_id)

    if subscribed_user:
      interaction.client.db.remove_subscribed_user(user_id)
      title = Msg.ALERTS_OFF_TITLE
      description = Msg.ALERTS_OFF
      color = 0xff0000  # Red
    else:
      interaction.client.db.add_subscribed_user(user_id, threshold=threshold)
      title = Msg.ALERTS_ON_TITLE
      description = Msg.ALERTS_ON
      color = 0x00ff00  # Green

    embed = discord.Embed(title=title, description=description, color=color)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    logger.info('User %s used the "toggle" command.', user_id)
  # pylint: disable=broad-except
  except Exception as e:
    logger.error('The "toggle" command failed for user %s. %s', user_id, str(e))
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)

def setup(bot):
  """
  Add the toggle command to the bot's command tree.

  Args:
    bot: The bot instance to add the command to.
  """
  bot.tree.add_command(toggle)
