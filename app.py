from flask import Flask, render_template, jsonify, request
import feedparser
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import sqlite3
import time
import threading

app = Flask(__name__)

RSS_FEEDS = [
    "https://money.cnn.com/services/rss/",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.foxnews.com/story/foxnews-com-rss-feeds",
    "https://www.sec.gov/about/rss-feeds",
    "https://www.federalreserve.gov/feeds/feeds.htm"
]

CATEGORY_MAP = {
    "Politics": [],
    "War": [],
    "Finance": [],
}

def create_connection():
    conn = sqlite3.connect('news.db')
    return conn

def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS articles
                        (title TEXT, link TEXT, summary TEXT, category TEXT)''')

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def fetch_and_scrape():
    while True:
        for feed in RSS_FEEDS:
            d = feedparser.parse(feed)
            for entry in d.entries:
                response = requests.get(entry.link)
                soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = soup.find_all('p')
                article_text = ' '.join([para.get_text() for para in paragraphs])
                
                # Summarize using Hugging Face transformers
                if len(article_text.split()) > 30:  # Check if there's enough text to summarize
                    summary = summarizer(article_text, max_length=100, min_length=30, do_sample=False)
                    summary_text = summary[0]['summary_text']
                else:
                    summary_text = article_text[:100] + "..."  # Fallback to truncating if text is too short

                category = categorize_article(entry.title)
                store_article(entry.title, entry.link, summary_text, category)

        time.sleep(5)  # fetch every 5 seconds

def categorize_article(title):
    if "finance" in title.lower():
        return "Finance"
    elif "war" in title.lower():
        return "War"
    else:
        return "Politics"

def store_article(title, link, summary, category):
    conn = create_connection()
    with conn:
        conn.execute("INSERT INTO articles (title, link, summary, category) VALUES (?, ?, ?, ?)",
                     (title, link, summary, category))

@app.route('/news', methods=['GET'])
def get_news():
    conn = create_connection()
    articles = conn.execute("SELECT * FROM articles").fetchall()
    return jsonify([{'title': row[0], 'link': row[1], 'summary': row[2], 'category': row[3]} for row in articles])

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    create_table()
    threading.Thread(target=fetch_and_scrape, daemon=True).start()
    app.run(debug=True)
