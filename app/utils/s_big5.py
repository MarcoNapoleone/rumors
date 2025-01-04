import numpy as np


def calculate_ocens(scores):
    """
    Calculate OCENS scores from an array of responses.

    Parameters:
        scores (list or numpy array): A list of 10 scores (1 to 5) corresponding to the following questions:

    "is reserved"
    "is generally trusting"
    "tends to be lazy"
    "is relaxed, handles stress well"
    "has few artistic interests"
    "is outgoing, sociable"
    "tends to find fault with others"
    "does a thorough job"
    "gets nervous easily"
    "has an active imagination"

    Returns:
        dict: A dictionary with keys 'Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'
              and their respective scores.
    """

    # Check if scores is a list of 10 elements
    if len(scores) != 10:
        raise ValueError("Scores must be a list of 10 elements")

    # Reverse scoring for specific items (scale: 1 -> 5, 2 -> 4, 3 -> 3, 4 -> 2, 5 -> 1)
    reverse_indices = [0, 2, 4, 6, 8]  # Questions to reverse
    reversed_scores = np.array(scores)
    reversed_scores[reverse_indices] = 6 - reversed_scores[reverse_indices]

    # Calculate OCENS traits
    openness = (reversed_scores[4] + scores[9]) / 2
    conscientiousness = (reversed_scores[2] + scores[7]) / 2
    extraversion = (reversed_scores[0] + scores[5]) / 2
    agreeableness = (scores[1] + reversed_scores[6]) / 2
    neuroticism = (scores[3] + reversed_scores[8]) / 2

    return {
        "Openness": openness,
        "Conscientiousness": conscientiousness,
        "Extraversion": extraversion,
        "Agreeableness": agreeableness,
        "Neuroticism": neuroticism
    }
