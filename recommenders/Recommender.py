

from typing import List
from Movie import Movie

class RecommenderInterface:
    def generate_recommendations(self, user_preference: dict[str, str]) -> dict[str, Movie]:
        pass
