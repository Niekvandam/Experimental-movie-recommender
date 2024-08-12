from typing import List
from pydantic import BaseModel


class UserProfile(BaseModel):
    """The UserProfile class is used to store user metadata for generating recommendations. \n
    Used for FastAPI and Streamlit to standardize the user metadata. 

    Args:
        BaseModel (_type_): The BaseModel class is used to define the structure of the UserProfile class.
    """
    genres: List[str] = [""]
    themes: List[str] = ["Space", "Love", "Action"]
    actors: List[str] = [""]
    directors: List[str] = [""]
    recent_watches: List[str] = ["Chopping Mall"]
    other_comments: str = "I like movies with robots"
    
    def to_metadata_str(self) -> str:
        """Returns a string representation of the user profile metadata. Used for generating embeddings.

        Returns:
            str: A string representation of the user profile metadata. Separated by newlines.
        """
        attribute_dump = self.model_dump()
        metadata_str = ""
        
        for key in attribute_dump:
            metadata_str += f"{key} -> {attribute_dump[key]}\n"
        return metadata_str