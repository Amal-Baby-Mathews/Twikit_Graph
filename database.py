# database.py
import sqlite3

DB_NAME = 'tweets.db'

def init_db():
    """Initializes the database and creates the 'tweets' table if it doesn't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                id TEXT PRIMARY KEY,
                author_name TEXT NOT NULL,
                author_username TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                search_topic TEXT NOT NULL
            )
        ''')
        conn.commit()
    print("✅ Database initialized successfully.")

def add_tweet(tweet_data):
    """Adds a classified tweet to the database, ignoring duplicates."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO tweets (id, author_name, author_username, text, created_at, sentiment, search_topic)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            tweet_data['id'],
            tweet_data['author_name'],
            tweet_data['author_username'],
            tweet_data['text'],
            tweet_data['created_at'],
            tweet_data['sentiment'],
            tweet_data['search_topic']
        ))
        conn.commit()
