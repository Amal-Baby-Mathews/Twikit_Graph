# app.py

import streamlit as st
import asyncio

from twitter_client import Twitter
from knowledge_graph import KnowledgeGraph

# --- Page Configuration ---
st.set_page_config(page_title="Twitter Sentiment Graph", layout="wide")


# --- Helper function to run asyncio code in Streamlit ---
def run_async(coro):
    """A helper to run async functions in the Streamlit event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# --- Session State Initialization ---
if 'client' not in st.session_state:
    st.session_state.client = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


# --- UI Sidebar for Login ---
with st.sidebar:
    st.title("🔐 Twitter Login")
    
    # --- Manual Login Form ---
    st.markdown("##### Manual Login")
    st_user = st.text_input("Username")
    st_email = st.text_input("Email / Phone")
    st_pass = st.text_input("Password", type="password")

    # --- Login Buttons ---
    col1, col2 = st.columns(2)
    
    # Manual Login Button
    with col1:
        if st.button("Login", use_container_width=True):
            if st_user and st_email and st_pass:
                with st.spinner("Logging in..."):
                    try:
                        client_instance = Twitter()
                        # Call login with the form credentials
                        st.session_state.client = run_async(
                            client_instance.login(st_user, st_email, st_pass)
                        )
                        st.session_state.logged_in = True
                    except Exception as e:
                        st.error(f"Login failed: {e}")
                        st.session_state.logged_in = False
            else:
                st.warning("Please fill in all login fields.")

    # Default Login Button (for debugging)
    with col2:
        if st.button("Default", help="Login with credentials from your .env file", use_container_width=True):
            with st.spinner("Logging in with default credentials..."):
                try:
                    client_instance = Twitter()
                    # Call login with NO arguments to use .env file
                    st.session_state.client = run_async(client_instance.login())
                    st.session_state.logged_in = True
                except Exception as e:
                    st.error(f"Default login failed: {e}")
                    st.session_state.logged_in = False

    st.divider()
    if st.session_state.logged_in:
        st.success("✅ Logged in")
    else:
        st.info("Please log in to search for tweets.")

# --- Main Page UI ---
st.title("🐦 Twitter Sentiment Knowledge Graph")
st.markdown("Visualize the sentiment and connections around a topic on Twitter/X.")

if st.session_state.logged_in:
    topic = st.text_input("Enter a topic to analyze:", "AI ethics")
    num_tweets = st.slider("Number of tweets to fetch:", 10, 100, 25)
    
    if st.button("Generate Graph"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Fetching tweets and building knowledge graph..."):
                try:
                    # Fetch tweets using the logged-in client
                    tweets = run_async(st.session_state.client.client.search_tweet(
                        topic, 'Latest', count=num_tweets
                    ))
                    
                    # Build the graph, passing the topic to the constructor
                    kg = KnowledgeGraph(topic=topic)
                    kg.build_from_tweets(tweets)
                    
                    # Generate and display the graph HTML
                    graph_html = kg.generate_html()
                    st.components.v1.html(graph_html, height=800, scrolling=True)

                except Exception as e:
                    st.error(f"An error occurred: {e}")
else:
    st.warning("Please log in using the sidebar to proceed.")