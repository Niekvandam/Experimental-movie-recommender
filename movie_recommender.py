import streamlit as st

from movie_data.tmdb import get_genres, get_actors, get_keyword_ids, discover_movies
from dotenv import load_dotenv
from settings import AMOUNT_OF_MOVIES

from recommenders.SubtitleRecommender import SubtitleRecommender
from recommenders.OpenAIRecommender import AIAssistRecommender, PureAIRecommender
from recommenders.WorstMovieRecommender import  WorstMovieRecommender

import logging
from data.explanation import recommendation_explanation
from user_profile import UserProfile
st.set_page_config(layout="wide")
# Set up logging
logging.basicConfig(level=logging.INFO)

FullAIRecommender = PureAIRecommender()
AiAssistRecommender = AIAssistRecommender()
FunRecommender = WorstMovieRecommender() # very fun recommender
SRTRecommender = SubtitleRecommender()

if "movie_dict" not in st.session_state:
    st.session_state.recommended_movies = {}

user_profile = UserProfile()

# Load .env file
if not load_dotenv():
    st.error("Could not load .env file, please make sure it exists in the root directory of the project.")

actor_dict = get_actors()
genre_dict = get_genres()

def parse_form(recommendation_system, user_profile):
    print(f"user profile {user_profile}")
    recommended_movies = get_recommendation_system(recommendation_system).generate_recommendations(user_profile)
    # Filter movies with self.validated = True
    recommended_movies = {movie: details for movie, details in recommended_movies.items() if details.validated}
    st.session_state.movies_dict = recommended_movies
   
    
def get_recommendation_system(recommendation_system):
    if recommendation_system == "Pure AI":
        return FullAIRecommender
    elif recommendation_system == "AI-Assisted":
        return AiAssistRecommender
    elif recommendation_system == "Subtitle embeddings":
        return SRTRecommender
    elif recommendation_system == "Worst wikipedia movies":
        return FunRecommender
    else:
        return FullAIRecommender
    
def update_user_profile():
    user_profile.genres = genres
    user_profile.actors = selected_actors
    user_profile.directors = directors
    user_profile.recent_watches = recent_watches.split(',')
    user_profile.themes = themes
    user_profile.other_comments = other_comments


user_profile = UserProfile()


# Streamlit form
st.subheader("User Preferences")
recommendation_system = st.sidebar.selectbox("Recommendation System", ["Pure AI", "AI-Assisted", "Worst wikipedia movies", "Subtitle embeddings"])
st.sidebar.write(recommendation_explanation)
# Create two columns for user input
col1, col2 = st.columns(2)
with col1:
    genres = st.multiselect("Preferred Genres", genre_dict.keys())
    actors = st.multiselect("Favorite Actors", actor_dict.keys())
    directors = st.text_input("Favorite Directors")
    

with col2:
    recent_watches = st.text_input("Recent Watches")
    themes = st.text_input("Favorite Themes", "Friendship, Love, Programming")
    other_comments = st.text_input("Additional Preferences")


selected_actors = [actor_dict[actor] for actor in actors]
selected_genres = [genre_dict[genre] for genre in genres]

user_profile.genres = genres
user_profile.actors = actors
user_profile.directors = directors
user_profile.recent_watches = recent_watches.split(',')
user_profile.themes = themes.split(',')
user_profile.other_comments = other_comments

# Button to generate recommendations
submitted = st.button("Get Recommendations", on_click=parse_form, args=(recommendation_system, user_profile))
    
    
# Function to display movie details in a pop-up
def display_movie_details(movie, details):
    st.write(f"**Genre:** {details.genre}")
    st.write(f"**Director:** {details.director}")
    st.write(f"**Actors:** {details.actors}")
    st.write(f"**Why?** {details.reason}")
    st.write(f"**Plot:** {details.plot}")
    st.write(f"**IMDb Rating:** {details.imdbrating}")
    st.write(f"**Runtime:** {details.runtime}")
    st.write(f"**Language:** {details.language}")
    st.write(f"**Country:** {details.country}")

# Display movie posters and names with expanders
if submitted or "movies_dict" in st.session_state:
    if st.session_state.movies_dict != {}:
        cols = st.columns(4)
        for i, (movie, details) in enumerate(st.session_state.movies_dict.items()):
            with cols[i % 4]:
                try:
                    st.image(details.poster, use_column_width=True)
                    with st.expander(f"{details.title} ({details.year})"):
                        display_movie_details(movie, details)
                except Exception as e:
                    # No image available
                    logging.error(e)
                    logging.error(f"No data available for movie {movie}")