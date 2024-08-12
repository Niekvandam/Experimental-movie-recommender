from settings import WORST_WIKIPEDIA_URL
recommendation_explanation = f"""

## Pure AI
Uses OpenAI's GPT-3-5 to generate movie recommendations based on user preferences.

## AI-Assisted
Uses TMDB and OMDB to find movies based on the preferences. Aftewards, we finetune the list with OpenAI's GPT-3-5. 

## Worst wikipedia movies
Uses [the worst movies of all time from wikipedia]({WORST_WIKIPEDIA_URL}) as a base for recommendations. The plot of each movie is embedded and compared to the user's preferences.

## Subtitle embeddings
**EXPERIMENTAL** Uses subtitle embeddings to recommend movies based on user preferences. Keep in mind, you can have a theme and genre in mind, but the subtitles might not reflect that.

## Notes
- Might take a few seconds to load
- Separate your preferences with a comma
- The more information you provide, the 'better' the recommendations
- Will only recommend 5 movies per request
- The 'Worst wikipedia movies' is wikipedia's opinion, not mine :)
"""