# main.py
import asyncio
from prompt_toolkit import PromptSession
from rich.console import Console
from rich.table import Table
from rich.text import Text

import database
import sentiment_analyzer
from twitter_client import Twitter

async def run_analysis():
    """Main function to run the CLI and the analysis pipeline."""
    # --- Initialization ---
    database.init_db()
    console = Console()
    twitter = Twitter()
    session = PromptSession()

    try:
        await twitter.login()
    except Exception as e:
        console.print(f"[bold red]❌ Login Failed:[/bold red] {e}")
        console.print("Please check your credentials in the .env file.")
        return

    # --- Main Application Loop ---
    while True:
        try:
            topic = await session.prompt_async(
                'Enter a topic to analyze (or type "exit" to quit): '
            )
            if topic.lower() == 'exit':
                break
            if not topic:
                continue

            with console.status("[bold green]Fetching and analyzing tweets...[/]") as status:
                tweets = await twitter.search(topic)
                
                classified_tweets = {'Positive': [], 'Negative': [], 'Neutral': []}

                for tweet in tweets:
                    sentiment = sentiment_analyzer.classify_sentiment(tweet.text)
                    tweet_data = {
                        'id': tweet.id,
                        'author_name': tweet.user.name,
                        'author_username': tweet.user.screen_name,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'sentiment': sentiment,
                        'search_topic': topic
                    }
                    database.add_tweet(tweet_data)
                    classified_tweets[sentiment].append(tweet_data)

            # --- Display Results ---
            console.rule(f"[bold blue]Sentiment Analysis for '{topic}'[/bold blue]")

            for sentiment, color in [("Positive", "green"), ("Negative", "red"), ("Neutral", "yellow")]:
                table = Table(
                    title=Text(f"{sentiment} Tweets", style=f"bold {color}"),
                    show_header=True,
                    header_style=f"bold {color}"
                )
                table.add_column("Author", style="cyan", no_wrap=True)
                table.add_column("Tweet Text", style="magenta")
                
                tweets_list = classified_tweets[sentiment]
                if not tweets_list:
                    table.add_row(f"No {sentiment.lower()} tweets found.", "")
                else:
                    for t in tweets_list:
                        author_info = f"{t['author_name']}\n(@{t['author_username']})"
                        table.add_row(author_info, t['text'].strip().replace('\n', ' '))
                
                console.print(table)
                
        except (KeyboardInterrupt, EOFError):
            break # Allow exiting with Ctrl+C or Ctrl+D
        except Exception as e:
            console.print(f"[bold red]An error occurred:[/bold red] {e}")

    console.print("\n👋 Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(run_analysis())
    except ImportError:
        print("\nVADER lexicon not found. Please run `import nltk; nltk.download('vader_lexicon')` in a Python shell.")
