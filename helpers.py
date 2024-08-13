from typing import Dict, List
import numpy as np
from auth import get_openai_client
from settings import EMBEDDING_MODEL
from user_profile import UserProfile
import json
import logging


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def create_preference_embedding(user_profile: UserProfile) -> List[float]:
    """Creates an embedding string from the user profile and returns the embedding data.

    Args:
        user_profile (UserProfile): The user profile to embed

    Returns:
        List[float]: Returns an embedding arary
    """
    metadata = user_profile.to_metadata_str()
    return create_text_embedding(metadata)

def create_text_embedding(text: str) -> List[float]:
    response = get_openai_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    # Extract the embedding data from the response
    return response.data[0].embedding

def load_json_data(path) -> Dict[str, dict]:
    """Loads the data from a JSON file.

    Returns:
        Dict[str, dict]: _description_
    """
    try:
        logging.debug("Loading data from %s", path)
        with open(path, 'r') as json_file:
            return json.load(json_file)
    except Exception as e:
        logging.error(f"An error occurred while loading data: {e}")
        return {}