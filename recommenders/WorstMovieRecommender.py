import logging
import os
import requests
import json

from typing import Dict
from bs4 import BeautifulSoup
from Movie import Movie
from recommenders.Recommender import RecommenderInterface
from settings import WIKIPEDIA_JSON_PATH, AMOUNT_OF_MOVIES, WORST_WIKIPEDIA_URL
from helpers import cosine_similarity, create_preference_embedding, create_text_embedding, load_json_data
from user_profile import UserProfile

class WikipediaMovieFetcher:
    def __init__(self, url: str):
        self.url = url
    
    def fetch_movies(self) -> Dict[str, dict]:
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = {}
        movie_name = ""
        for element in soup.find_all(['h3', 'p'])[3:-1]: # Last one is 'works cited'
            if element.name == 'h3':
                movie_name = element.text.strip()
                movies[movie_name] = {}
            elif element.name == 'p' and movie_name in movies:
                movies[movie_name]["plot"] = element.text.strip()
        return movies

class JsonDataHandler:
    """Handles the loading and saving of JSON data for the worst movies of all time. 
    Is different from SubtitleLoader.py due to different internal structure.  
    """
    def __init__(self, path: str):
        self.path = path
    

    
    def save_data(self, data: Dict[str, dict]) -> bool:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logging.error(f"An error occurred while saving data: {e}")
            return False

class WorstMovieRecommender(RecommenderInterface):
    """My implementation of a movie recommender system based on the worst movies of all time from wikipedia. 
    Args:
        RecommenderInterface (_type_): The recommender interface which this class implements.
    """
    def __init__(self) -> None:
        self.json_data_handler = JsonDataHandler(path=WIKIPEDIA_JSON_PATH)
        self.movie_fetcher = WikipediaMovieFetcher(url=WORST_WIKIPEDIA_URL)
     
        # Check if the JSON file exists, if not fetch the data and save it to a JSON file.
        json_file_path = self.json_data_handler.path
        if os.path.exists(json_file_path):
            self.wikipedia_movies = load_json_data(json_file_path)
        else:
            self.wikipedia_movies = self._fetch_and_embed_movies()
            self.json_data_handler.save_data(self.wikipedia_movies)
        
    def _fetch_and_embed_movies(self) -> Dict[str, dict]:
        """Fetches the movies from the wikipedia page and embeds the plot of each movie.

        Returns:
            Dict[str, dict]: A list of movies with their respective plots and embeddings.
        """
        movies = self.movie_fetcher.fetch_movies()
        for movie, data in movies.items():
            embedding = create_text_embedding(data["plot"])
            movies[movie]["embedding"] = embedding
        return movies


    def generate_recommendations(self, user_profile: UserProfile) -> Dict[str, Movie]:
        """Parse the user profile, compare it to the wikipedia movies and return the top movies.

        Args:
            user_profile (UserProfile): A user profile object containing the user's preferences.

        Returns:
            Dict[str, Movie]: The top movies based on the user's preferences.
        """
        # Create an embedding of the user profile
        user_profile_embedding = create_preference_embedding(user_profile)

        # Compare the user profile embedding to the wikipedia movies
        movie_similarities = []
        for movie, data in self.wikipedia_movies.items():
            similarity = cosine_similarity(user_profile_embedding, data["embedding"])
            movie_similarities.append((movie, similarity))
        
        # Sort the movies by similarity and get the top movies. x[1] is the similarity score, as the list is a tuple (movie, similarity)
        movie_similarities.sort(key=lambda x: x[1], reverse=True)
        top_movies = [movie for movie, _ in movie_similarities[:AMOUNT_OF_MOVIES]]
        
        # Create a dictionary of the top movies
        movie_dict = {}
        for movie_name in top_movies:
            movie_name_clean = movie_name.strip()
            title, year = map(str.strip, movie_name_clean.split('(', 1))
            year = year.split(')', 1)[0]
            movie = Movie(title=title, year=year, user_profile=user_profile)
            movie_dict[movie_name] = movie
            
        return movie_dict
