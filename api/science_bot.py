# api/post-science.py
# Vercel Python handler: Ignores request, runs bot logic, returns success/error

import os
import tweepy
import requests
import random
import datetime
import io
from http.server import BaseHTTPRequestHandler

# X API Keys from Vercel Env Vars
client = tweepy.Client(
    bearer_token=os.getenv("BEARER"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET")
)

facts = [
    "A teaspoon of neutron star weighs 110 million tons 🌑",
    "Octopuses have three hearts and blue blood 🐙",
    "Your body replaces ~330 billion cells every day",
    "More trees on Earth (3 trillion) than stars in the Milky Way (100–400 billion) 🌳",
    "Quantum entanglement: particles linked faster than light ⚛",
]

def get_nasa_apod():
    try:
        r = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY").json()
        return r["url"], r["title"] if r["media_type"] == "image" else (None, None)
    except: return None, None

def run_bot():
    if random.random() < 0.7:  # 70% chance with image
        url, title = get_nasa_apod()
        if url:
            caption = f"Astronomy Picture of the Day ✨\n{title}\n\n#NASA #Space #Science"
            media_url = url
        else:
            caption = f"Daily Science Fact 🤖\n\n{random.choice(facts)}\n\n#Science #Bot"
            media_url = None
    else:
        caption = f"Daily Science Fact 🤖\n\n{random.choice(facts)}\n\n#Science #Space"
        media_url = None

    try:
        if media_url:
            img = requests.get(media_url).content
            media = client.media_upload(filename="img.jpg", file=io.BytesIO(img))
            client.create_tweet(text=caption, media_ids=[media.media_id])
        else:
            client.create_tweet(text=caption)
        return f"Posted at {datetime.datetime.now()}! Tweet: {caption[:50]}..."
    except Exception as e:
        raise e  # Let Vercel log it

class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # Cron hits GET
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        try:
            result = run_bot()
            self.wfile.write(result.encode())
        except Exception as e:
            self.send_response(500)
            self.wfile.write(str(e).encode())
