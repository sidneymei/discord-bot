import discord
from discord import app_commands
from logger import log_cmd, log_err
from msg import Msg
import time

@app_commands.command(name="ping", description=Msg.CMD_DESC_PING)
async def ping_command(interaction: discord.Interaction):
  try:
    start = time.perf_counter()
    
    embed = discord.Embed(title=Msg.PING_INITIAL, color=0x00bfff)
    embed.set_footer(text=Msg.PING_FOOTER)

    await interaction.response.send_message(embed=embed)
    
    end = time.perf_counter()
    latency = (end - start) * 1000
    embed.title = Msg.PING_RESULT.format(latency=latency)
    
    await interaction.edit_original_response(embed=embed)
    log_cmd(interaction.user.id, "ping")
  except Exception as e:
    log_err(f"Error in ping command: {str(e)}")
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)

def setup(bot):
  bot.tree.add_command(ping_command)