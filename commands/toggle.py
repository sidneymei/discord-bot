import discord
from discord import app_commands
from logger import log_cmd, log_err
from msg import Msg

@app_commands.command(name="toggle", description=Msg.CMD_DESC_TOGGLE)
async def toggle_command(interaction: discord.Interaction):
  """
  Toggle the price alert subscription for a user.

  This command allows users to subscribe or unsubscribe from price alerts.

  Args:
    interaction (discord.Interaction): The interaction object representing the command invocation.
  """
  user_id = interaction.user.id

  try:
    subscribed_users = interaction.client.db.get_subscribed_users()

    if user_id in subscribed_users:
      interaction.client.db.remove_subscribed_user(user_id)
      title = Msg.ALERTS_OFF_TITLE
      description = Msg.ALERTS_OFF
      color = 0xff0000  # Red
    else:
      interaction.client.db.add_subscribed_user(user_id)
      title = Msg.ALERTS_ON_TITLE
      description = Msg.ALERTS_ON
      color = 0x00ff00  # Green

    embed = discord.Embed(title=title, description=description, color=color)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    log_cmd(user_id, "toggle")
  # pylint: disable=broad-except
  except Exception as e:
    log_err(f"Error in toggle command for user {user_id}: {str(e)}")
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)

def setup(bot):
  """
  Add the toggle command to the bot's command tree.

  Args:
    bot: The bot instance to add the command to.
  """
  bot.tree.add_command(toggle_command)
