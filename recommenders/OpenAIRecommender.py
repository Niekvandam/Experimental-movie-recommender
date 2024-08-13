import json
import streamlit as st

from typing import Dict, List
from Movie import Movie
from auth import get_openai_client
from recommenders.Recommender import RecommenderInterface
from movie_data.tmdb import discover_movies
from settings import AMOUNT_OF_MOVIES as amount
from user_profile import UserProfile

def send_openai_request(prompt: str) -> str:
    """Sends request to OpenAI's chat endpoint and returns the response.

    Args:
        prompt (str): The prompt to send to the OpenAI API.

    Returns:
        str: The response from the OpenAI API.
    """
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a movie expert that provides detailed movie recommendations in JSON format."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096
    )
    return response.choices[0].message.content

def parse_recommendations(recommendations: str) -> Dict[str, Movie]:
    """Parses the recommendation from OpenAI's response.
    Is always in JSON format, so we can parse it directly.

    Args:
        recommendations (str): List of movie recommendations in JSON format.

    Returns:
        Dict[str, Movie]: A dictionary with the movie title as key and the Movie object as value.
    """
    try:
        print(recommendations)
        movie_list = json.loads(recommendations).get('movies', [])
        movie_dict = {}
        for movie in movie_list:
            # Turn movie from json into a Movie object
            cur_movie = Movie(title=movie['title'], explanation=movie['explanation'])
            movie_dict[movie['title']] = cur_movie
        return movie_dict
    except Exception as e:
        st.error(f"An error occurred while parsing the recommendations: {e} \n Please try again!")
        
        return {}

def build_prompt(user_profile: UserProfile, current_movies: List = []) -> str:
    prompt = (
        f"The user likes movies with the following genres: {user_profile.genres}. "
        f"Their favorite themes are: {user_profile.themes}. "
        f"They enjoy movies with actors like: {user_profile.actors}. "
        f"Their favorite directors are: {user_profile.directors}. "
        f"Recently, they watched: {user_profile.recent_watches}. DO NOT recommend these movies again."
        f"Other comments: {user_profile.other_comments}. "
    )
    if current_movies != []:
        movie_list = ', '.join(movie['original_title'] for movie in current_movies)
        prompt += (
            f"Currently we have this list of movies: [{movie_list}]. "
            "You are allowed to modify the list of movies if you think it will help the user. "
            "Additionally, add extra movies if the list is not exhaustive enough yet. "
        )
    prompt += (
        "Return a list of movies that the user would like, taking all preferences into account where possible."
        "Return the list in JSON format with the title (in english) and a 3-sentence HONEST explanation why the user would like this movie."
        "Example format: {\"movies\": [{\"title\": \"Movie title\", \"explanation\": \"Explanation why user would like this movie.\"}]} "
        f"Recommend at least {amount} movies. Be creative in recommendations, honest in explanations"
    )
    return prompt


# Yes, this could've been a single class with a parameter to determine if it should use the current movies or not.

class AIAssistRecommender(RecommenderInterface):
    """AIAssistRecommender is a recommender that uses OpenAI's chat endpoint to generate movie recommendations based on user preferences.
    Difference with PureAIRecommender is that this one uses the current movies to generate recommendations.

    Args:
        RecommenderInterface (_type_): The recommender interface which this class implements.
    """
    def generate_recommendations(self, user_profile: UserProfile) -> Dict[str, Movie]:
        current_movies = discover_movies(user_profile)
        prompt = build_prompt(user_profile=user_profile, current_movies=current_movies)
        recommendations = send_openai_request(prompt)
        return parse_recommendations(recommendations)

class PureAIRecommender(RecommenderInterface):
    """PureAIRecommender is a recommender that uses OpenAI's chat endpoint to generate movie recommendations based on user preferences.
    It does not use the discover movies function generate recommendations.

    Args:
        RecommenderInterface (_type_): The recommender interface which this class implements.
    """
    def generate_recommendations(self, user_profile: UserProfile) -> Dict[str, Movie]:
        prompt = build_prompt(user_profile=user_profile)
        recommendations = send_openai_request(prompt)
        return parse_recommendations(recommendations)
