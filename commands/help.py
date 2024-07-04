import discord
from discord import app_commands
from logger import log_cmd, log_err
from msg import Msg

@app_commands.command(name="help", description=Msg.CMD_DESC_HELP)
async def help_command(interaction: discord.Interaction):
  try:
    embed = discord.Embed(title=Msg.HELP_TITLE, color=0x00bfff)
    
    for cmd in interaction.client.tree.walk_commands():
      embed.add_field(name=f"/{cmd.name}", value=cmd.description, inline=False)
    
    await interaction.response.send_message(embed=embed)
    log_cmd(interaction.user.id, "help")
  except Exception as e:
    log_err(f"Error in help command for user {interaction.user.id}: {str(e)}")
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)

def setup(bot):
  bot.tree.add_command(help_command)