class Msg:
  """
  A class containing constant messages used throughout the bot.

  This class provides a centralized location for all string constants
  used in various parts of the bot, including command descriptions,
  alert messages, and error messages.
  """

  # Unicode cent symbol
  CENT_SYMBOL = '\xa2'

  # Command descriptions
  CMD_DESC_HELP = "Display a list of available commands and their descriptions"
  CMD_DESC_PING = "Check {bot_name}'s server response time"
  CMD_DESC_TOGGLE = "Enable or disable alerts for when prices cross the ComEd basic electric service price threshold"
  CMD_DESC_CHECK = "View the current hourly average electricity price"

  # Help command messages
  HELP_TITLE = "{bot_name} Commands"

  # Price alert messages
  PRICE_TITLE = "{price:.1f}{cent} per kWh"
  PRICE_DESCRIPTION = "ComEd electricity prices are currently {status}. {detail}"
  PRICE_FOOTER = "{difference:.1f}{cent} {direction} than the ComEd basic electric service price of {threshold:.1f}{cent}"

  # Price status messages
  PRICE_LOW = "low"
  PRICE_MODERATE = "moderate"
  PRICE_HIGH = "high"

  # Price detail messages
  PRICE_LOW_DETAIL = "This is a good time to use electricity-intensive appliances."
  PRICE_MODERATE_DETAIL = "Consider moderate usage of high-consumption devices."
  PRICE_HIGH_DETAIL = "It's advisable to limit use of non-essential electrical appliances."

  # Toggle command messages
  ALERTS_OFF_TITLE = "Price Alerts Turned Off"
  ALERTS_OFF = "You will no longer receive notifications about electricity price changes."
  ALERTS_ON_TITLE = "Price Alerts Turned On"
  ALERTS_ON = "You'll be notified when electricity prices change significantly compared to the ComEd basic electric service price."

  # Error messages
  CMD_ERR = "An error occurred while processing the command."
  PERM_ERR = "You don't have permission to use this command."
  COMED_PRICE_ERR = "Failed to retrieve ComEd price."

  # Other messages
  CHECK_COOLDOWN = "Please wait before checking the price again."
