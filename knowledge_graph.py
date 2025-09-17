# knowledge_graph.py

import networkx as nx
from pyvis.network import Network
from collections import defaultdict
import sentiment_analyzer

class KnowledgeGraph:
    """
    Builds a hierarchical knowledge graph for a specific topic.
    
    The structure is:
    Topic -> Sentiment -> Tweet -> User
                     ^
                     |
                   Hashtag (links related tweets)
    """
    def __init__(self, topic):
        self.topic = topic
        self.graph = nx.Graph()

    def _add_central_topic_node(self):
        """Adds the main topic node, which acts as the graph's root."""
        self.graph.add_node(
            self.topic,
            label=self.topic,
            title=f"Central Topic: {self.topic}",
            shape='star',
            color='#FF5733',
            size=35
        )

    def _add_sentiment_nodes(self):
        """Adds the three core sentiment nodes and connects them to the topic."""
        sentiments = {
            "Positive": "#28a745",
            "Negative": "#dc3545",
            "Neutral": "#ffc107"
        }
        for sentiment, color in sentiments.items():
            self.graph.add_node(
                sentiment,
                label=sentiment,
                title=f"Sentiment: {sentiment}",
                shape='diamond',
                color=color,
                size=25
            )
            # Edge: Topic -> links to -> Sentiment
            self.graph.add_edge(self.topic, sentiment)
            
    def build_from_tweets(self, tweets):
        """
        Main method to build the graph from a list of tweet objects.
        It creates a hierarchical structure and links related tweets.
        """
        # Reset graph and build the core structure
        self.graph.clear()
        self._add_central_topic_node()
        self._add_sentiment_nodes()

        # A map to find tweets that share the same hashtag
        hashtag_to_tweets = defaultdict(list)

        # --- First Pass: Build the primary Topic -> Sentiment -> Tweet -> User hierarchy ---
        for tweet in tweets:
            sentiment = sentiment_analyzer.classify_sentiment(tweet.text)
            tweet_id = f"tweet_{tweet.id}"
            user_id = f"user_{tweet.user.screen_name}"

            # Add Tweet Node
            self.graph.add_node(
                tweet_id,
                label="Tweet",
                title=tweet.text,
                shape='square',
                color=self.graph.nodes[sentiment]['color'], # Inherit color from parent
                size=15
            )
            # Edge: Sentiment -> contains -> Tweet
            self.graph.add_edge(sentiment, tweet_id)

            # Add User Node
            if not self.graph.has_node(user_id):
                self.graph.add_node(
                    user_id,
                    label=tweet.user.name,
                    title=f"@{tweet.user.screen_name}\nFollowers: {tweet.user.followers_count}",
                    shape='dot',
                    color='#1DA1F2',
                    size=20
                )
            # Edge: Tweet -> posted by -> User
            self.graph.add_edge(tweet_id, user_id)

            # Populate the hashtag map for the second pass
            if tweet.hashtags:
                for ht in tweet.hashtags:
                    hashtag_to_tweets[ht.lower()].append(tweet_id)
        
        # --- Second Pass: Automatically connect related nodes via common hashtags ---
        for hashtag, tweet_ids in hashtag_to_tweets.items():
            if len(tweet_ids) > 1:  # Only link if hashtag is shared by multiple tweets
                hashtag_id = f"hashtag_{hashtag}"
                self.graph.add_node(
                    hashtag_id,
                    label=f"#{hashtag}",
                    title=f"Shared Theme: #{hashtag}",
                    shape='triangle',
                    color='#794BC4',
                    size=12
                )
                # Edge: Connect all related tweets to this common hashtag node
                for tweet_id in tweet_ids:
                    self.graph.add_edge(tweet_id, hashtag_id)

    def generate_html(self, filename="sentiment_graph.html"):
        """
        Generates an interactive HTML file from the NetworkX graph using Pyvis.
        """
        net = Network(height='800px', width='100%', notebook=True, cdn_resources='in_line')
        net.from_nx(self.graph)
        
        # Apply physics options for a better layout
        net.show_buttons(filter_=['physics'])
        html=net.generate_html(filename, notebook=False)
        with open("graph_output.html", "w", encoding="utf-8") as file:
            file.write(html)
        return html