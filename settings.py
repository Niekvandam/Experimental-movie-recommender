OMDB_URL = "http://www.omdbapi.com/"
TMDB_URL = "https://api.themoviedb.org/3/"
TMDB_DISCOVERY_URL = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc"
WORST_WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_films_considered_the_worst"

AMOUNT_OF_MOVIES = 5

WIKIPEDIA_JSON_PATH = "data/json/worst_movies.json"
SRT_JSON_PATH = "data/json/subtitles.json"
SRT_PATH = "data/subtitles/"
# The minute interval used to split SRT files by
SRT_INTERVAL = 10 

# TODO fix consistency of amount of movies used


OPENAI_MODEL = "gpt-3.5-turbo-1106" # Alternatively, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini

# Alternatively, text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002
# PLEASE NOTE: embedding models are UNIQUE in their output. Meaning that if a different model is used,
# the .json files will have to be removed and re-generated. Otherwise, the subtitles and worst movie recommender will not work
# as the cosine similarity can't be calculated.
EMBEDDING_MODEL = "text-embedding-3-small" 