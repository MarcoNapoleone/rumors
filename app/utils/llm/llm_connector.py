import json

import requests

from app.utils.llm.llm_adapter import ResponseAdapter
from app.utils.settings import Config


def query_llm(system_prompt, user_prompt):
    """
    Query the LLM with the given system and user prompts.

    Args:
        system_prompt: The system prompt to configure the LLM.
        user_prompt: The user prompt containing the specific task.

    Returns:
        The response from the LLM as a dictionary.
    """
    headers = {'Content-Type': 'application/json'}

    if Config.LLM_ENDPOINT_TYPE == 'openrouter':
        url = Config.LLM_URL
        headers["Authorization"] = f"Bearer {Config.OPENROUTER_KEY}"

        data = {
            "model": Config.LLM_MODEL,
            "temperature": 0.5,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

    elif Config.LLM_ENDPOINT_TYPE == 'ollama':
        url = Config.LLM_URL

        data = {
            "model": Config.LLM_MODEL,
            "temperature": Config.LLM_TEMPERATURE,
            "messages": [
                {
                    "role": "user",
                    "content": f"{system_prompt}\n{user_prompt}",
                }
            ],
            "stream": False
        }

    else:
        raise ValueError("Invalid LLM_ENDPOINT_TYPE. Please set it to 'openrouter' or 'ollama'.")

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return ResponseAdapter(response.json(), Config.LLM_ENDPOINT_TYPE, user_prompt).to_dict()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def explain_recommendation(rated_items, item_to_recommend, personality_traits=None):
    """
    Generate personalized movie recommendations based on user ratings and Big 5 personality traits.

    Args:
        rated_movies: Dict or list of previously rated movies.
        movie_to_recommend: String name of the movie to recommend.
        personality_traits: Dict containing Big 5 personality scores (openness, conscientiousness,
                            extraversion, agreeableness, neuroticism).

    Returns:
        The response from the LLM as a dictionary.
        :param personality_traits:
        :param item_to_recommend:
        :param rated_items:
    """

    system_prompt = "You are a helpful assistant."

    if personality_traits:
        recommendation_prompt = f""" Briefly explain to the users why they might enjoy the movie: {item_to_recommend}. 
        You may used the following information: the users rated the following movies between 1 and 5 like this: {rated_items} and their personality traits between 1 and 5 are {personality_traits}.
        Speak directly to the user in English that is easily accessible to non-native speakers.  """
    else:
        recommendation_prompt = f""" Briefly explain to the users why they might enjoy the movie: {item_to_recommend}. 
        You may used the following information: the users rated the following movies between 1 and 5 like this: {rated_items}. 
            Speak directly to the user in English that is easily accessible to non-native speakers. """

    return query_llm(system_prompt, recommendation_prompt)
