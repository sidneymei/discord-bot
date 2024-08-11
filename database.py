import sqlite3

class Database:
  """
  A class to handle database operations for subscribed users.
  """

  def __init__(self, db_path):
    """
    Initialize the Database object.

    Args:
      db_path (str): The path to the SQLite database file.
    """
    self.db_path = db_path
    self.init_db()

  def init_db(self):
    """
    Initialize the database by creating the necessary table if it doesn't exist.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('''CREATE TABLE IF NOT EXISTS subscribed_users
                        (user_id INTEGER PRIMARY KEY)''')
      conn.commit()

  def get_subscribed_users(self):
    """
    Retrieve all subscribed user IDs from the database.

    Returns:
      list: A list of user IDs (integers) of subscribed users.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT user_id FROM subscribed_users')
      return [row[0] for row in cursor.fetchall()]

  def add_subscribed_user(self, user_id):
    """
    Add a new user to the subscribed users list.

    Args:
      user_id (int): The ID of the user to be added.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('INSERT OR IGNORE INTO subscribed_users (user_id) VALUES (?)', (user_id,))
      conn.commit()

  def remove_subscribed_user(self, user_id):
    """
    Remove a user from the subscribed users list.

    Args:
      user_id (int): The ID of the user to be removed.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('DELETE FROM subscribed_users WHERE user_id = ?', (user_id,))
      conn.commit()
