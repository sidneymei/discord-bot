import discord
from discord import app_commands
from logger import log_cmd, log_err
from msg import Msg

@app_commands.command(name="help", description=Msg.CMD_DESC_HELP)
async def help_command(interaction: discord.Interaction):
  """
  Display a list of available commands and their descriptions.

  This command creates an embed message containing all registered commands
  and their descriptions.

  Args:
    interaction (discord.Interaction): The interaction object representing the command invocation.
  """
  try:
    embed = discord.Embed(title=Msg.HELP_TITLE.format(bot_name=interaction.client.user.name), color=0x00bfff)

    for cmd in interaction.client.tree.walk_commands():
      embed.add_field(name=f"/{cmd.name}", value=cmd.description, inline=False)

    await interaction.response.send_message(embed=embed)
    log_cmd(interaction.user.id, "help")
  # pylint: disable=broad-except
  except Exception as e:
    log_err(f"Error in help command for user {interaction.user.id}: {str(e)}")
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)

def setup(bot):
  """
  Add the help command to the bot's command tree.

  Args:
    bot: The bot instance to add the command to.
  """
  bot.tree.add_command(help_command)
