import discord
import aiohttp
from bs4 import BeautifulSoup

from msg import Msg
from logger import logger

def get_color(price):
  """
  Determine the color based on the price.

  Args:
    price (float): The current electricity price.

  Returns:
    int: A hexadecimal color code.
  """
  if price < 5:
    return 0x00ff00  # Green
  elif 5 <= price <= 14:
    return 0xff9900  # Orange
  else:
    return 0xff0000  # Red

def get_price_info(price):
  """
  Get the price status and detail based on the price.

  Args:
    price (float): The current electricity price.

  Returns:
    tuple: A tuple containing the price status and detail.
  """
  if price < 5:
    return Msg.PRICE_LOW, Msg.PRICE_LOW_DETAIL
  elif 5 <= price <= 14:
    return Msg.PRICE_MODERATE, Msg.PRICE_MODERATE_DETAIL
  else:
    return Msg.PRICE_HIGH, Msg.PRICE_HIGH_DETAIL

def create_price_embed(price, price_to_compare):
  """
  Create a Discord embed for the price information.

  Args:
    price (float): The current electricity price.
    price_to_compare (float): The ComEd basic electric service price.

  Returns:
    discord.Embed: An embed containing formatted price information.
  """
  price_status, price_detail = get_price_info(price)
  price_difference = price - price_to_compare
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
    threshold=price_to_compare
  ))
  return embed

async def fetch_comed_price_to_compare(url):
  """
  Fetch the ComEd basic electric service price from the provided URL.

  Args:
    url (str): The URL to fetch the price from.

  Returns:
    float or None: The fetched price, or None if unsuccessful.
  """
  async with aiohttp.ClientSession() as session:
    try:
      async with session.get(url) as response:
        if response.status == 200:
          html = await response.text()
          soup = BeautifulSoup(html, 'html.parser')
          
          # Find the first table in the document
          table = soup.find('table')
          if table:
            # Find the cell with the price (should be the second cell in the second row)
            rows = table.find_all('tr')
            if len(rows) >= 2:
              price_cell = rows[1].find_all('td')
              if len(price_cell) >= 1:
                # Extract the price value
                price_text = price_cell[0].text.strip()
                # Remove 'cents per kWh' and convert to float
                price_value = float(price_text.split()[0])
                return price_value
    except Exception as e:
      logger.error("Error fetching ComEd price to compare: %s" % str(e))
  return None
