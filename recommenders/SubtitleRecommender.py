import numpy as np
import pysrt
import json
import logging
import os

from typing import Dict
from Movie import Movie
from recommenders.Recommender import RecommenderInterface
from settings import SRT_JSON_PATH, SRT_PATH, SRT_INTERVAL
from auth import get_openai_client
from helpers import cosine_similarity, create_preference_embedding, create_text_embedding, load_json_data
from user_profile import UserProfile

class SubtitleLoader:
    """Loads subtitles from a specified folder and saves them to a JSON file for later use.
    If the JSON file already exists, it will load the subtitles from there instead of parsing the SRT files again.
    """
    def __init__(self, json_path: str, srt_path: str, client):
        self.json_path = json_path
        self.srt_path = srt_path
        self.client = client
    
    def load_subtitles(self) -> Dict[str, dict]:
        """Loads the subtitles from the JSON file if it exists, otherwise parses the SRT files and saves them to a JSON file.

        Returns:
            Dict[str, dict]: A keyvalue pair where key is movie name, and value is a dictionary of the movie subtitles, embeddings, chopped up in intervals of 10 minutes.
        """
        if os.path.exists(self.json_path):
            return load_json_data(self.json_path)
        else:
            subtitles = self._parse_srt_files(self.srt_path)
            self._save_to_json(subtitles, self.json_path)
            return subtitles
    
    def _save_to_json(self, subtitles: Dict[str, dict], path: str) -> bool:
        """If the JSON file does not exist, saves the subtitles to a JSON file. This is to prevent parsing the SRT files every time.

        Args:
            subtitles (Dict[str, dict]): The dictionary which has been created from the SRT files.
            path (str): Path to save it to. 

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as json_file:
                json.dump(subtitles, json_file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logging.error(f"unexpected error occurred whilst loading JSON: {e}")
            return False
    
    def _parse_srt_files(self, srt_folder: str) -> Dict[str, dict]:
        """Main method to parse the SRT files and create a dictionary of the subtitles and embeddings.
        Will loop through the determined folder and parse each SRT file using pysrt. 
        
        These will then be delegated to _parse_srt_file to create a dictionary per file. 

        Args:
            srt_folder (str): The folder where the SRT files are stored.

        Returns:
            Dict[str, dict]: Keyvaluepair where key is movie name, and value is a dictionary of the movie subtitles, embeddings, chopped up in intervals of 10 minutes.
        """
        parsed_movies = {}
        for file in os.listdir(srt_folder):
            if file.endswith('.srt'):
                title = file.split('.srt')[0]
                file_path = os.path.join(srt_folder, file)
                subs = pysrt.open(file_path)
                parsed_movies[title] = self._parse_srt_file(subs, title)
        return parsed_movies
    
    def _parse_srt_file(self, file: pysrt.SubRipFile, title: str) -> dict:
        """Parses a single SRT file and creates a dictionary of the subtitles and embeddings."""
        
        movie = {}
        interval_length = SRT_INTERVAL
        current_interval = 10
        current_text = ""
        
        # Create dictionary entry
        movie["title"] = title
        
        # Loop over subtitles in file. These are already an array thanks to pysrt
        for sub in file:
            # Convert the pysrt time to minutes
            start_time_minutes = sub.start.minutes + sub.start.hours * 60
            
            # Calculate the interval with floor division. 
            # If the interval is different, save the current text and start a new one.
            interval = start_time_minutes // interval_length
            if interval != current_interval:
                if current_text:
                    movie[current_interval]["text"] = current_text.strip()
                    
                # Update interval and text
                current_interval = interval
                current_text = ""
                
            # Append the text to the current text
            current_text += f" {sub.text}"
            
            # Create a new dictionary entry if this is a new interval
            if current_interval not in movie:
                movie[current_interval] = {}
        
        # Save the last text
        if current_text:
            movie[current_interval]["text"] = current_text.strip()
            
        # Loop over the intervals and create embeddings for the text
        for interval, data in movie.items():
            if isinstance(data, dict) and "text" in data:
                response = create_text_embedding(data["text"])
                movie[interval]["embedding"] = response
        return movie

class SubtitleRecommender(RecommenderInterface):
    """My experimental recommender. It uses subtitles embeddings from movies to recommend movies based on user preferences.
    This does not work 100%. It uses cosine similarity to compare the user profile to the embeddings of the subtitles.
    
    In order to use this recommender, you will either need to have the /data/json/subtitles.json file or the SRT files in the /data/subtitles folder.
    
    If you want to add more movies, you can add SRT files to the /data/subtitles folder, delete the /data/json/subtitles.json file and run the api or streamlit.
    If you add a subtitle, please use the format <title> <year>.srt. For example: "The Matrix (1999).srt"

    #TODO Make this recommender user friendly. Does not work well with the current setup.
    Args:
        RecommenderInterface (_type_): The basic recommender interface. Used for compatibility.
    """
    def __init__(self) -> None:
        subtitle_loader = SubtitleLoader(SRT_JSON_PATH, SRT_PATH, get_openai_client())
        self.subtitles = subtitle_loader.load_subtitles()
    
    def generate_recommendations(self, user_profile: UserProfile) -> Dict[str, Movie]:
        """Creates recommendations based on the user profile. It uses cosine similarity to compare the user profile to the embeddings of the subtitles.

        Args:
            user_profile (UserProfile): The UserProfile class that was provided 

        Returns:
            Dict[str, Movie]: returns an ordered dictionary of movies with the title as key and the Movie class as value.
        """
        # Create embedding for the user profile
        logging.debug("Generating recommendations based on subtitles")
        user_embedding = create_preference_embedding(user_profile)
        movie_scores = []
        
        # Loop over the subtitles and calculate the similarity
        for title, movie in self.subtitles.items():
            interval_embeddings = [
                data["embedding"] for interval, data in movie.items() if isinstance(data, dict) and "embedding" in data
            ]
            if not interval_embeddings:
                continue
            similarities = [cosine_similarity(user_embedding, np.array(embedding)) for embedding in interval_embeddings]
            average_similarity = np.mean(similarities)
            # Append the title and average similarity to the movie_scores list
            movie_scores.append((title, average_similarity))
            
        logging.debug("Recommendation scores calculated")
        # Sort it by the similarity. This is [x[1]] because the tuple is (title, similarity)
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        logging.debug("Recommendations sorted")
        logging.debug("The top 5 recommendations are:")
        for title, score in movie_scores[:5]:
            logging.debug("%s: %s", title, score)
            
        movie_dict = {}
        
        logging.debug("Creating Movie classes for recommendations")
        # Create a Movie class for each movie and add it to the movie_dict
        for movie_name, score in movie_scores:
            movie_name_clean = movie_name.strip()
            title, year = map(str.strip, movie_name_clean.split('(', 1))
            year = year.split(')', 1)[0]
            movie = Movie(title=title, year=year, user_profile=user_profile)
            movie_dict[movie_name] = movie
        return movie_dict
