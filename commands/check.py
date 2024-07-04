import discord
from discord import app_commands
from logger import log_cmd, log_err
from msg import Msg
from utils import create_price_embed

class CheckCooldown:
  def __init__(self, rate, per):
    self.rate = rate
    self.per = per
    self.last_check = {}

  def is_on_cooldown(self, user_id):
    import time
    current_time = time.time()
    if user_id in self.last_check:
      elapsed = current_time - self.last_check[user_id]
      return elapsed < self.per
    return False

  def update_cooldown(self, user_id):
    import time
    self.last_check[user_id] = time.time()

cooldown = CheckCooldown(rate=1, per=60)  # 1 use per 60 seconds

@app_commands.command(name="check", description=Msg.CMD_DESC_CHECK)
async def check_command(interaction: discord.Interaction):
  user_id = interaction.user.id
  
  if cooldown.is_on_cooldown(user_id):
    await interaction.response.send_message(Msg.CHECK_COOLDOWN, ephemeral=True)
    return

  try:
    current_price = await interaction.client.get_comed_price()
    
    if current_price is not None:
      embed = create_price_embed(current_price, interaction.client.PRICE_THRESHOLD)
      await interaction.response.send_message(embed=embed, ephemeral=True)
      log_cmd(user_id, "check")
      cooldown.update_cooldown(user_id)
    else:
      await interaction.response.send_message(Msg.COMED_PRICE_ERR, ephemeral=True)
  except Exception as e:
    log_err(f"Error in check command for user {user_id}: {str(e)}")
    await interaction.response.send_message(Msg.CMD_ERR, ephemeral=True)

def setup(bot):
  bot.tree.add_command(check_command)