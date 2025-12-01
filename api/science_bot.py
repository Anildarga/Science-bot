import os
import tweepy
import requests
import random
import datetime
import io

# ----- TWITTER AUTH -----
client = tweepy.Client(
    bearer_token=os.getenv("BEARER"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET")
)

# ----- UNSPLASH -----
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")

# ----- OPENAI -----
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

facts = [
    "A teaspoon of neutron star weighs 110 million tons 🌑",
    "Octopuses have three hearts and blue blood 🐙",
    "Your body replaces ~330 billion cells every day",
    "More trees on Earth (3 trillion) than stars in the Milky Way (100–400 billion) 🌳",
    "Quantum entanglement: particles linked faster than light ⚛",
]

def nasa_apod():
    try:
        r = requests.get(
            "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        ).json()
        if r.get("media_type") == "image":
            return r["url"], r["title"]
    except:
        pass
    return None, None


def unsplash_image():
    try:
        r = requests.get(
            f"https://api.unsplash.com/photos/random?query=science&client_id={UNSPLASH_KEY}"
        ).json()
        return r["urls"]["regular"], r.get("alt_description", "Science Image")
    except:
        return None, None


def dalle_image():
    if not OPENAI_KEY:
        return None, None

    try:
        headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
        data = {
            "model": "gpt-image-1",
            "prompt": "A stunning science-themed image for a daily science tweet."
        }
        r = requests.post("https://api.openai.com/v1/images", json=data, headers=headers).json()
        return r["data"][0]["url"], "AI-generated Science Art"
    except:
        return None, None


def run_bot():
    # Choose the image source randomly
    source = random.choice(["nasa", "unsplash", "openai", "none"])

    url = title = None
    caption = ""

    if source == "nasa":
        url, title = nasa_apod()
        caption = f"NASA Astronomy Picture of the Day ✨\n{title}\n\n#NASA #Space #Science"

    elif source == "unsplash":
        url, title = unsplash_image()
        caption = f"Science Photo of the Day 🔬\n{title}\n\n#Unsplash #Science"

    elif source == "openai":
        url, title = dalle_image()
        caption = f"AI-Generated Science Art 🤖✨\n{title}\n\n#AI #Dalle #Science"

    # If no image source works → fallback fact
    if not url:
        caption = f"Daily Science Fact 🤖\n\n{random.choice(facts)}\n\n#Science #Space"
    
    try:
        if url:
            img = requests.get(url).content
            media = client.media_upload(filename="img.jpg", file=io.BytesIO(img))
            client.create_tweet(text=caption, media_ids=[media.media_id])
        else:
            client.create_tweet(text=caption)
        return f"[OK] Posted at {datetime.datetime.now()} with source: {source}"
    except Exception as e:
        return f"[ERROR] {str(e)}"


# ----- REQUIRED FOR VERCEL ----- #
def handler(request):
    result = run_bot()
    return {
        "statusCode": 200,
        "body": result
    }
