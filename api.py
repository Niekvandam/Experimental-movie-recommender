from typing import List
from enum import Enum
from typing import List
from fastapi import FastAPI
from recommenders.SubtitleRecommender import SubtitleRecommender
from recommenders.OpenAIRecommender import AIAssistRecommender, PureAIRecommender
from recommenders.WorstMovieRecommender import  WorstMovieRecommender
from movie_data.tmdb import get_genres, get_actors, get_keyword_ids, discover_movies
from movie_data.omdb import get_movie_by_title
from dotenv import load_dotenv
from fastapi import FastAPI
from movie_data.omdb import get_movie_by_title
from dotenv import load_dotenv
import uvicorn
from user_profile import UserProfile    

app = FastAPI()

    
class RecommendationSystem(str, Enum):
    SUBTITLES = "subtitles"
    AIASSIST = "aiassist"
    PUREAI = "pureai"
    WORSTMOVIE = "worstmovie"

@app.post("/recommend/{system}", tags=["Recommendations"])
def recommend(system: RecommendationSystem, user_profile: UserProfile):
    if system == RecommendationSystem.SUBTITLES:
        recommender = SubtitleRecommender()
    elif system == RecommendationSystem.AIASSIST:
        recommender = AIAssistRecommender()
    elif system == RecommendationSystem.PUREAI:
        recommender = PureAIRecommender()
    elif system == RecommendationSystem.WORSTMOVIE:
        recommender = WorstMovieRecommender()
    else:
        return {"error": "Invalid recommendation system"}

    recommendations = recommender.generate_recommendations(user_profile=user_profile)
    return {"recommendations": recommendations}

@app.get("/movies/genres", tags=["Movie data"])
def get_movie_genres():
    genres = get_genres()
    return {"genres": genres}

@app.get("/movies/actors", tags=["Movie data"])
def get_movie_actors():
    actors = get_actors()
    return {"actors": actors}

@app.post("/movies/keywords", tags=["Movie data"])
def get_movie_keywords(keywords: List[str]):
    keyword_ids = get_keyword_ids()
    return {"keyword_ids": keyword_ids}

@app.post("/movies/discover", tags=["Movie data"])
def discover_movie(user_profile: UserProfile):
    movies = discover_movies()
    return {"movies": movies}

@app.post("/movies/{title}", tags=["Movie data"])
def get_movie_by_title(title: str):
    movie = get_movie_by_title(title)
    return {"movie": movie}

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn    
    load_dotenv()
    uvicorn.run(app, host="127.0.0.1", port=8000)
    