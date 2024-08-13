from auth import get_openai_client
from settings import OMDB_URL
from user_profile import UserProfile
from settings import OPENAI_MODEL

import os
import logging
import requests
import wikipediaapi

omdb_api_key = os.getenv('OMDB_API_KEY')
client = get_openai_client()

class MovieChoiceExplainer():
    def explain_movie(self, movie, user_profile: UserProfile, ) -> str:
        """Generates a short explanation of why the user would like the movie based on the user profile metadata."""        
        metadata = user_profile.to_metadata_str()
        explanation = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a movie expert that provides compact movie recommendations. Take a deep breath, and let's get started!"},
                {"role": "system", "content": f"Movie plot: {movie.longer_plot}"},
                {"role": "user", "content": f"Explain why the user would like the movie: {movie.title}. The plot is provided. Be honest, but keep it short. User profile: {metadata}"}
            ],
            max_tokens=200
        )
        return explanation.choices[0].message.content.strip()

class MovieDataRetriever():
    def get_movie_by_title(self, title: str, year: str = None) -> dict | None:
        """Tries to get a movie by title and year from the OMDB API.

        Args:
            title (str): The title of the movie.
            year (str, optional): The year of the movie. Defaults to None as not every movie comes provided with one

        Returns:
            dict | None: Returns the movie data from OMDB or None if the movie is not found.
        """
        response = requests.get(OMDB_URL, params={"apikey": omdb_api_key, "t": title, "plot": "full", "y": year})
        data = response.json()
        if data['Response'] == "True":
            data['Plot'] = self.summarize_plot(data['Plot'])
            return data
        else:
            logging.error("Movie not found: %s", title)
            return None
    
    def get_longer_plot(self, title) -> str | None:
        """Ideally, we would like to get a longer plot from Wikipedia. This is because the OMDB plot is often too short for a comprehensive explanation / summary. 

        Args:
            title (_type_): The title of the movie. Needed for wikipedia search.

        Returns:
            str: The plot, extracted from Wikipedia.
        """
        wiki_wiki = wikipediaapi.Wikipedia(user_agent='movie-recommender',language='en')
        page = wiki_wiki.page(f"{title}")
        if page.exists():
            plot_section = page.section_by_title('Plot')
            if plot_section:
                plot_text = plot_section.text
                if len(plot_text) > 2500:
                    plot_text = plot_text[:2500]
                return plot_text
        return None
    
    def summarize_plot(self, plot: str) -> str:
        """Summarizes the provided plot using GPT-3.5-turbo.

        Args:
            plot (str): The plot to summarize

        Returns:
            str: _description_
        """
        logging.debug("Summarizing plot with AI")
        prompt = (f"Summarize the following plot:\n\n{plot}")
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that has in-depth movie knowledge."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

movie_data_retriever = MovieDataRetriever()
movie_choice_explainer = MovieChoiceExplainer()

class Movie():
    def __init__(self, title: str, explanation: str = None, year: int =None, user_profile: UserProfile = None) -> None:
        self.movie_data_retriever = movie_data_retriever
        self.movie_choice_explainer = movie_choice_explainer
        self.title = title
        self.reason = explanation
        self.year = year
        self.genre = None
        self.director = None
        self.plot = None
        self.awards = None
        self.country = None
        self.language = None
        self.imdbrating = None
        self.runtime = None
        self.released = None
        self.actors = None
        self.longer_plot = None
        self.user_profile_used = user_profile
        
        # TODO fix this code, convoluted
        # Gets movie by title and year, then uses the response to set all above attributes in set_attributes
        self.set_attributes(self.movie_data_retriever.get_movie_by_title(title=title, year=year))
        
        # If the response is not None, it will continue 
        if self.validated:
            
            # Retrieve longer plot from wikipedia if possible, and summarize it
            self.longer_plot = self.movie_data_retriever.get_longer_plot(self.title)
            if self.longer_plot:
                self.plot = self.movie_data_retriever.summarize_plot(self.longer_plot)
            
            else:
                # If we can't retrieve it, summarize it from the 3 lines of IMDB plot
                self.plot = self.movie_data_retriever.summarize_plot(self.plot)
                
            if self.reason is None and self.user_profile_used is not None:
                # If no reason has been given yet, we create our own!
                self.reason = self.movie_choice_explainer.explain_movie(self, self.user_profile_used)

    def set_attributes(self, data: dict | None) -> None:
        """Write the data to the Movie instance attributes.

        Args:
            data (dict): A dictionary of movie data from OMDB.
        """
        # Loop over all data, and set it as its own attribute. 
        if data is None:
            self.validated = False
            return
        for key, value in data.items():
            attr_name = key.lower().replace(" ", "_")
            setattr(self, attr_name, value)    
        self.validated = True
    
    def print_attributes(self):
        """Print all attributes of the Movie instance."""
        for attr, value in self.__dict__.items():
            print(f"{attr}: {value}")