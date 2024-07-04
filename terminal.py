import aioconsole
from logger import log_cmd, log_err
from msg import Msg

class Terminal:
  def __init__(self, bot):
    self.bot = bot

  async def start(self):
    while True:
      cmd = await aioconsole.ainput("Enter command: ")
      should_continue = await self.process_cmd(cmd)
      if not should_continue:
        break

  async def process_cmd(self, cmd):
    if cmd == "reload":
      await self.reload_commands()
    elif cmd == "test_comed":
      await self.test_comed()
    elif cmd == "exit":
      print(Msg.SHUTDOWN)
      await self.bot.close()
      return False
    else:
      print(Msg.UNKNOWN_CMD)
    return True

  async def reload_commands(self):
    try:
      self.bot.tree.clear_commands(guild=None)
      await self.bot.load_commands()
      await self.bot.tree.sync()
      print(Msg.CMDS_RELOADED)
      log_cmd("TERMINAL", "reload")
    except Exception as e:
      log_err(f"Error reloading commands: {str(e)}")
      print(Msg.RELOAD_ERR)

  async def test_comed(self):
    price = await self.bot.get_comed_price()
    if price is not None:
      print(Msg.COMED_PRICE_INFO.format(price=price, threshold=self.bot.PRICE_THRESHOLD))
      log_cmd("TERMINAL", "test_comed")
    else:
      print(Msg.COMED_PRICE_ERR)