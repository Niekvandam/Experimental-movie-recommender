import os
import openai
import logging

def get_themoviedb_headers() -> dict[str, str]:
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ['TMDB_API_KEY']}"
    }
    
def get_openai_client() -> openai.Client:
    return openai.Client(
        api_key=os.environ['OPENAI_API_KEY']
    )