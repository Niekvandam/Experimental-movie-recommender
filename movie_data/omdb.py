import requests
import os
import logging

from auth import get_openai_client
from settings import OMDB_URL, OPENAI_MODEL

omdb_api_key = os.getenv('OMDB_API_KEY')
client = get_openai_client()

def get_movie_by_title(title: str, year: str = None) -> dict | None:
    logging.info("Validating movie: %s",title)
    response = requests.get(OMDB_URL, params={"apikey": omdb_api_key, "t": title, "plot": "full", "y": year}) 
    data = response.json()
    if data['Response'] == "True":
        data['Plot'] = _summarize_plot(data['Plot'])
        return data
    logging.error("Movie not found: %s", title)
    return None

def _summarize_plot(plot: str) -> str:
    logging.debug("Summarizing plot -> %s", plot)
    prompt = (f"Summarize the following plot:\n\n{plot}")
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides detailed movie recommendations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()