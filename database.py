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
      cursor.execute(
        '''CREATE TABLE IF NOT EXISTS subscribed_users
                    (user_id INTEGER PRIMARY KEY,
                     threshold REAL)
        ''')
      conn.commit()

  def get_subscribed_users(self):
    """
    Retrieve all subscribed user IDs from the database.

    Returns:
      list: A list of tuples (user_id, threshold) of subscribed users.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT user_id, threshold FROM subscribed_users')
      return cursor.fetchall()
    
  def get_subscribed_user(self, user_id):
    """
    Retrieve all subscribed user IDs from the database.

    Returns:
      list: A list of tuples (user_id, threshold) of subscribed users.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT user_id, threshold FROM subscribed_users WHERE user_id = ?', (user_id,))
      return cursor.fetchone()

  def add_subscribed_user(self, user_id, threshold=None):
    """
    Add a new user to the subscribed users list.

    Args:
      user_id (int): The ID of the user to be added.
      threshold (float, optional): The price threshold for alerts. Defaults to None.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('INSERT OR IGNORE INTO subscribed_users (user_id, threshold) VALUES (?, ?)', (user_id, threshold))
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

  def get_user_threshold(self, user_id):
    """
    Get the threshold for a specific user.

    Args:
      user_id (int): The ID of the user.

    Returns:
      float or None: The user's threshold if set, otherwise None.
    """
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT threshold FROM subscribed_users WHERE user_id = ?', (user_id,))
      result = cursor.fetchone()
      return result[0] if result else None
