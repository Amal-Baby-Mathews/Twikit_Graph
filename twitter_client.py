# twitter_client.py
import os
from twikit import Client
from dotenv import load_dotenv

load_dotenv()


# --- Custom Exceptions for Clearer Error Handling ---
class TwitterLoginError(Exception):
    """Custom exception for login failures."""
    pass

class TwitterSearchError(Exception):
    """Custom exception for search failures."""
    pass


class Twitter:
    def __init__(self):
        self.client = Client('en-US')
        # Load credentials from .env as a fallback
        self.default_username = os.getenv('TWITTER_USERNAME')
        self.default_email = os.getenv('TWITTER_EMAIL')
        self.default_password = os.getenv('TWITTER_PASSWORD')

    async def login(self, username=None, email=None, password=None):
        """
        Logs into Twitter using provided credentials, or falls back to .env file.
        Raises TwitterLoginError on failure.
        """
        auth_user = username if username else self.default_username
        auth_email = email if email else self.default_email
        auth_pass = password if password else self.default_password

        print(f"Attempting to log in as '{auth_user}'...")
        try:
            await self.client.login(
                auth_info_1=auth_user,
                auth_info_2=auth_email,
                password=auth_pass,
                cookies_file='cookies.json'
            )
            print("✅ Login successful!")
            return self  # Return self for chaining or storing the instance
    
        except Exception as e:
            # A catch-all for any other unexpected errors
            raise TwitterLoginError(f"An unexpected error occurred during login: {e}")


    async def search(self, topic: str, count: int = 20):
        """
        Searches for a given number of latest tweets on a topic.
        Raises TwitterSearchError on failure.
        """
        print(f"🔎 Searching for '{topic}'...")
        try:
            tweets = await self.client.search_tweet(topic, 'Latest', count=count)
            return tweets
        
        # --- Exception Handling ---
        except TwikitHTTPError as e:
            # Catches network issues or if the search query is invalid
            raise TwitterSearchError(f"A network error occurred during search. The topic might be invalid or Twitter/X is unavailable. Original error: {e}")
        except Exception as e:
            # A catch-all for any other unexpected errors
            raise TwitterSearchError(f"An unexpected error occurred during search: {e}")