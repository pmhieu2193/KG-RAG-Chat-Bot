import sqlite3
from datetime import datetime
import config

class ChatHistory:
    def __init__(self):
        self.db_path = config.SQLITE_DB_PATH
        self.init_database()

    def init_database(self):
        """Initialize database and create table if it doesn't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")

    def add_conversation(self, question, answer):
        """Add a new conversation to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO chat_history (question, answer, time)
                    VALUES (?, ?, ?)
                ''', (question, answer, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding conversation: {e}")
            return False

    def get_all_history(self):
        """Retrieve all chat history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT question, answer, time FROM chat_history ORDER BY time DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving history: {e}")
            return []

    def clear_history(self):
        """Clear all chat history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM chat_history')
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error clearing history: {e}")
            return False