from flask import Flask, jsonify, render_template
import feedparser
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import sqlite3
import time
import threading

app = Flask(__name__)

# Define RSS feeds
RSS_FEEDS = [
    "https://money.cnn.com/services/rss/",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.foxnews.com/story/foxnews-com-rss-feeds",
    "https://www.sec.gov/about/rss-feeds",
    "https://www.federalreserve.gov/feeds/feeds.htm"
]

# Category mapping for articles
CATEGORY_MAP = {
    "Politics": [],
    "War": [],
    "Finance": [],
}

# Database connection functions
def create_connection():
    conn = sqlite3.connect('news.db')
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS articles
                        (title TEXT, link TEXT, summary TEXT, category TEXT)''')

# Initialize summarization pipeline
summarizer = pipeline("summarization")

# Function to fetch and scrape news articles
def fetch_and_scrape():
    while True:
        for feed in RSS_FEEDS:
            d = feedparser.parse(feed)
            for entry in d.entries:
                response = requests.get(entry.link)
                soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = soup.find_all('p')
                article_text = ' '.join([para.get_text() for para in paragraphs])

                # Check if the article text is long enough to summarize
                if len(article_text.split()) > 10:
                    # Summarize using Hugging Face transformers
                    summary = summarizer(article_text, max_length=100, min_length=30, do_sample=False)
                    summary_text = summary[0]['summary_text']
                else:
                    summary_text = article_text  # Use the full text if it's too short

                category = categorize_article(entry.title)
                store_article(entry.title, entry.link, summary_text, category)

        time.sleep(600)  # Fetch every 10 minutes

# Function to categorize articles based on title
def categorize_article(title):
    title_lower = title.lower()
    if "finance" in title_lower:
        return "Finance"
    elif "war" in title_lower:
        return "War"
    else:
        return "Politics"

# Function to store articles in the database
def store_article(title, link, summary, category):
    conn = create_connection()
    with conn:
        conn.execute("INSERT INTO articles (title, link, summary, category) VALUES (?, ?, ?, ?)",
                     (title, link, summary, category))

# API endpoint to get news articles
@app.route('/news', methods=['GET'])
def get_news():
    conn = create_connection()
    articles = conn.execute("SELECT * FROM articles").fetchall()
    return jsonify([{'title': row['title'], 'link': row['link'], 'summary': row['summary'], 'category': row['category']} for row in articles])

# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

# Start the application
if __name__ == '__main__':
    create_table()
    threading.Thread(target=fetch_and_scrape, daemon=True).start()
    app.run(debug=True)
