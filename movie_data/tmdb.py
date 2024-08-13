import requests
import streamlit as st
import logging

from typing import List
from auth import get_themoviedb_headers
from settings import TMDB_URL, TMDB_DISCOVERY_URL
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

def build_tmdb_discover_url(user_profile: UserProfile) -> str:
    """Build the discover movie URL from TMDB. We use this to find movies based on the user profile.
    Is very prone to returning 0 results if the filters are too diverse. Therefore it is recommended
    to split up the user profile and search for actors and themes separately.

    Args:
        user_profile (UserProfile): the profile to filter on

    Returns:
        _type_: the URL to send to TMDB
    """
    url = TMDB_DISCOVERY_URL
    
    # For each of the filters, we need to check if they are not empty. If they are, we skip them.
    # If not, we add them to the URL. However, first we need to get the correct ID's for the filters.
    
    # All values are appended with a | to make sure the filters are OR filters. 
    if user_profile.genres != []:
        genre_dict = get_genres()
        genres = '|'.join(map(str, [genre_dict[genre] for genre in user_profile.genres]))
        url += f"&with_genres={genres}"
        
    if user_profile.themes != ['']:
        keyword_ids = get_keyword_ids(user_profile.themes)
        keywords = '|'.join(map(str, keyword_ids))
        url += f"&with_keywords={keywords}"
        
    if user_profile.actors != []:
        actor_dict = get_actors()
        actors = '|'.join(map(str, [actor_dict[actor] for actor in user_profile.actors]))
        url += f"&with_cast={actors}"
        
    return url

def discover_movies(user_profile: UserProfile) -> List:
    """Discover movies based on the user profile. This function will first try to find movies based on the full user profile.
    If it doesn't manage to find any movies, it will split the user profile into actors and themes and try to find movies based on those.

    Args:
        user_profile (UserProfile): The user profile to filter on

    Returns:
        List: A list of 'discovered' movies that match the user profile
    """
    url = build_tmdb_discover_url(user_profile)
    data = send_discovery_request(url)
    
    # If no movies are found, we split the user profile into actors and themes and try again.
    if data == []:
        actor_profile, themes_profile = split_user_profile(user_profile)
        url = build_tmdb_discover_url(actor_profile)
        data = send_discovery_request(url)
        url = build_tmdb_discover_url(themes_profile)
        data.update(send_discovery_request(url))
        
    # If still no movies are found, we return an empty list.
    if data == []:
        st.write("No movies found with these filters")
        return []
    
    return data

def send_discovery_request(url: str) -> dict:
    """For convenience reasons we split the request into a separate function. This function sends a request to the TMDB API
    This cannot be used for the other requests, since not all of them reutrn 'results'. 

    Args:
        url (str): the URL to send to the TMDB API

    Returns:
        dict: a dictionary with the the discovered movies
    """
    response = requests.get(url, headers=get_themoviedb_headers())
    data = response.json()
    if data.get('results') == []:
        return []
    else:
        return data['results']
    
def split_user_profile(user_profile: UserProfile):
    """TMDB is very picky in their filters. Incompatible actors / themes will result in 0 matches. Therefore it can be
    beneficial to look for these separately. 

    Args:
        user_profile (UserProfile): The userProfile to filter on
    """
    actor_user_profile = UserProfile(actors=user_profile.actors)
    theme_and_genre_user_profile = UserProfile(genres=user_profile.genres, themes=user_profile.themes)
    return (actor_user_profile, theme_and_genre_user_profile)