import discord
from msg import Msg

def get_color(price):
  if price < 5:
    return 0x00ff00  # Green
  elif 5 <= price <= 14:
    return 0xff9900  # Orange
  else:
    return 0xff0000  # Red

def get_price_info(price):
  if price < 5:
    return Msg.PRICE_LOW, Msg.PRICE_LOW_DETAIL
  elif 5 <= price <= 14:
    return Msg.PRICE_MODERATE, Msg.PRICE_MODERATE_DETAIL
  else:
    return Msg.PRICE_HIGH, Msg.PRICE_HIGH_DETAIL

def create_price_embed(price, threshold):
  price_status, price_detail = get_price_info(price)
  price_difference = price - threshold
  direction = "higher" if price_difference > 0 else "lower"

  embed = discord.Embed(
    title=Msg.PRICE_TITLE.format(price=price, cent=Msg.CENT_SYMBOL),
    description=Msg.PRICE_DESCRIPTION.format(status=price_status, detail=price_detail),
    color=get_color(price)
  )
  embed.set_footer(text=Msg.PRICE_FOOTER.format(
    difference=abs(price_difference),
    cent=Msg.CENT_SYMBOL,
    direction=direction,
    threshold=threshold
  ))
  return embed