import asyncio
from twikit import Client
from dotenv import load_dotenv
import os
load_dotenv()
USERNAME = os.getenv('TWITTER_USERNAME', 'your_username')
EMAIL = os.getenv('TWITTER_EMAIL')
PASSWORD = os.getenv('TWITTER_PASSWORD', 'your_password')

# Initialize client
client = Client('en-US')

async def main():
    print(f"Logging in...with {USERNAME}, {EMAIL}")
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD,
        cookies_file='cookies.json'
    )
    tweets = await client.search_tweet('python', 'Latest')

    for tweet in tweets:
        print(
            tweet.user.name,
            tweet.text,
            tweet.created_at
        )
asyncio.run(main())