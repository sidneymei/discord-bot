import sqlite3

class Database:
  def __init__(self, db_path):
    self.db_path = db_path
    self.init_db()

  def init_db(self):
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('''CREATE TABLE IF NOT EXISTS subscribed_users
                        (user_id INTEGER PRIMARY KEY)''')
      conn.commit()

  def get_subscribed_users(self):
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT user_id FROM subscribed_users')
      return [row[0] for row in cursor.fetchall()]

  def add_subscribed_user(self, user_id):
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('INSERT OR IGNORE INTO subscribed_users (user_id) VALUES (?)', (user_id,))
      conn.commit()

  def remove_subscribed_user(self, user_id):
    with sqlite3.connect(self.db_path) as conn:
      cursor = conn.cursor()
      cursor.execute('DELETE FROM subscribed_users WHERE user_id = ?', (user_id,))
      conn.commit()