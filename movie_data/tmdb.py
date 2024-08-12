import requests
from typing import List
from auth import get_themoviedb_headers
from settings import TMDB_URL, TMDB_DISCOVERY_URL
import logging
import streamlit as st

from user_profile import UserProfile


logging.basicConfig(level=logging.INFO)

def get_genres() -> List[str]:
    url = f"{TMDB_URL}genre/movie/list?language=en"
    response = requests.get(url, headers=get_themoviedb_headers())
    data = response.json()
    return {genre['name']: genre['id'] for genre in data['genres']}

def get_actors() -> List[str]:
    """ 
    Get a list of popular actors 
    Only returns top 20 "popular" actors, should be enough for demo purposes
    """
    url = f"{TMDB_URL}person/popular"
    response = requests.get(url, headers=get_themoviedb_headers())
    data = response.json()
    return  {actor['name']: actor['id'] for actor in data['results']}


def get_keyword_ids(keywords: List[str]) -> List[int]:
    """
    Get a list of keyword ids
    """
    keyword_ids = []
    
    for keyword in keywords:
        url = f"{TMDB_URL}search/keyword?query={keyword}&page=1"
        response = requests.get(url, headers=get_themoviedb_headers())
        data = response.json()
        try:
            keyword_ids.append(data['results'][0]['id'])
        except:
            logging.error(f"Keyword {keyword} not found")
    return keyword_ids

def build_tmdb_discover_url(user_profile: UserProfile):
    url = TMDB_DISCOVERY_URL
    
    if user_profile.genres != [""]:
        genre_dict = get_genres()
        genres = '|'.join(map(str, [genre_dict[genre] for genre in user_profile.genres]))
        url += f"&with_genres={genres}"
        
    if user_profile.themes != [""]:
        keyword_ids = get_keyword_ids(user_profile.themes)
        keywords = '|'.join(map(str, keyword_ids))
        url += f"&with_keywords={keywords}"
        
    if user_profile.actors != [""]:
        cast = '|'.join(map(str, user_profile.actors))
        url += f"&with_cast={cast}"
        
    if user_profile.directors != [""]:
        crew = '|'.join(map(str, user_profile.directors))
        url += f"&with_crew={crew}"
        
    return url

def discover_movies(user_profile: UserProfile) -> List:
    url = build_tmdb_discover_url(user_profile)
    logging.error(f"URL: {url}")
    response = requests.get(url, headers=get_themoviedb_headers())
    data = response.json()
    if data.get('results') == []:
        st.error("No movies found with the given criteria (this is really buggy sometimes?), switching to pure AI")
        return []
    else:
        return data['results']