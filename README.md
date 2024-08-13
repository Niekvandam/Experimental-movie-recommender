# Overview

Thanks for checking out my movie recommender!

## Recommenders
This repository contains four different ways of getting movies recommended to you! Let's quickly go over them below. 

### OpenAIRecommender
There are actually two different types of OpenAIRecommenders. One that is 'Pure' AI, and one that uses it as fallback.

#### PureAIRecommender
This recommender uses the user input, and parses it in OpenAI's GPT3-5 (turbo-1106). The response from OpenAI is then validated using The Open Movie Database (OMDB). Here we find metadata, movie poster and more. Afterwards we present it to the user. 

#### AIAssistRecommender
This recommender uses The Movie DataBase (TMDB) and The Open Movie Database (OMDB). This is due to the fact that Open Movie Database does not have a way to properly 'explore' movies based on the user input. This recommender uses the user input to search for relevant movies on TMDB using the theme, genre and actors. After it has retrieved the top selection of movies, we parse it through OpenAI to add, modify and rerank movies where necessary. Afterwards, we once again use OMDB to retrieve the metadata and present it to the end user.

### WorstMovieRecommender
This is where things get a bit more 'experimental'. While researching I stumbled across [This wiki page](https://en.wikipedia.org/wiki/List_of_films_considered_the_worst) and could not resist. I parsed this wiki page into separate entries and saved the data in the `/data/json/worst_movies.json` file. In order to compare these wiki pages to the user preference we use OpenAI's text-embedding-small embedding model to embed the description found on the wiki page. Afterwards, we use cosine similarity to compare this to the user input and find which ones are semantically similar. The ones with the highest similarity will be recommended. Additionally uses OMDB to validate movies and retrieve metadata. 

### SubtitleRecommender
Highly experimental recommender which embeds subtitles (.SRT) files. As SRT has timestamps we can use these to our advantage to get a more spread-out collection of embeddings. We split the text spoken into 10-minute intervals (can be changed in `settings.py` by updating SRT_INTERVAL). To recommend movies, we calculate the cosine similarity between all 10-minute subtitle chunks and the user-profile. We then average these out, and have our 'average' distance. 

I didn't have enough time to make this one work as desired, but is fun nonetheless. 

#### Adding your own subtitles
It's possible to add your own subtitles by downloading .srt files and adding them to the `/data/subtitles/` folder. However, in order to trigger a new update, you will have to remove `/data/json/subtitles.json`. During launch, it will detect the missing file and trigger a re-indexing of the subtitles. For best results, use `[movie-name] [movie-year].srt`. As this is the only pointer the file has to the movie it is referencing.  


# Getting started

## Installation
To run the codebase, you will need to have python3.10 or higher. Afterwards, you can run:
```
python -m pip install -r requirements.txt 
```
Optionally, you can create a .venv and execute it from there. 

Once it is properly installed, there are two ways of accessing the project. With FastAPI or Python 

## Setting up .env
As previously mentioned, we use OpenAI, OMDB and TMDB in this project. 

- **TMDB API key**: [Can be found here](https://developer.themoviedb.org/reference/intro/getting-started)
- **OMDB API key**: [Can be requested here](https://www.omdbapi.com/apikey.aspx)
- **OpenAI API key**: [Can be made here](https://platform.openai.com/api-keys)

These will need to be set, respsectively, in the `.env`. You can copy the `.env.example` as an example.

## Playing around with settings
Although somewhat unstable, you're able to play around with the `settings.py` file, and change up the `OPENAI_MODEL`, `EMBEDDING_MODEL`, and other fun stuff. Keep in mind that this has not been througoughly tested, and can be unstable.

## Running the API
Running the API from FastAPI is one command in the terminal from the root of the project. 
```
python api.py
```

The Swagger API will be ran on `http://localhost:8000/docs`

## Running Streamlit
To run the streamlit environment you will need to execute a python file from the streamlit package. This can be done by using
```
python -m streamlit run movie_recommender.py
```
The streamlit app can be found on `http://localhost:8501`