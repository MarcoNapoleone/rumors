from app.utils.settings import Config
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
import pickle
from pathlib import Path
from typing import Dict, List

# Path to store precomputed SVD data
SVD_STORAGE_PATH = Path("precomputed_svd.pkl")


def precompute_svd(k: int = 30) -> None:
    """
    Precomputes the SVD components and user ratings mean for the dataset
    and saves them to a pickle file.

    Args:
        k (int): Number of latent factors for SVD
    """
    # Load the dataset
    ratings = pd.read_csv(Config.RATINGS_PATH)

    # Create the user-movie matrix
    user_movie_matrix = ratings.pivot(
        index='userId',
        columns='movieId',
        values='rating'
    ).fillna(0)

    # Normalize ratings by subtracting the mean rating for each user
    user_ratings_mean = user_movie_matrix.mean(axis=1)
    matrix_norm = user_movie_matrix.sub(user_ratings_mean, axis=0)

    # Perform SVD
    U, sigma, Vt = svds(matrix_norm.values, k=k)
    sigma = np.diag(sigma)  # Convert diagonal array to matrix

    # Save precomputed components to pickle
    with open(SVD_STORAGE_PATH, "wb") as f:
        pickle.dump({
            "U": U,
            "sigma": sigma,
            "Vt": Vt,
            "user_ratings_mean": user_ratings_mean,
            "user_movie_matrix": user_movie_matrix
        }, f)

    print(f"SVD components precomputed and saved to {SVD_STORAGE_PATH}")

def load_precomputed_svd():
    """
    Loads the precomputed SVD components and user ratings mean from a pickle file.

    Returns:
        Dict: Dictionary containing SVD components and user-movie matrix
    """
    if not SVD_STORAGE_PATH.exists():
        raise FileNotFoundError(f"No precomputed SVD data found at {SVD_STORAGE_PATH}. Please run precompute_svd().")

    with open(SVD_STORAGE_PATH, "rb") as f:
        data = pickle.load(f)

    return data

def get_recommendation_items(new_user_ratings: Dict[str, float], top_n: int = 10) -> pd.Series:
    """
    Recommends movies for a new user based on collaborative filtering with SVD.

    Args:
        new_user_ratings (Dict[str, float]): Dictionary of {movie_id: rating} for the new user
        top_n (int): Number of recommendations to return

    Returns:
        pd.Series: Series of recommended movie_ids and their predicted ratings
    """
    # Load the dataset
    ratings = pd.read_csv(Config.RATINGS_PATH)

    # Create the user-movie matrix
    user_movie_matrix = ratings.pivot(
        index='userId',
        columns='movieId',
        values='rating'
    ).fillna(0)

    # Add the new user to the matrix
    new_user_id = user_movie_matrix.index.max() + 1
    new_user_row = pd.Series(0, index=user_movie_matrix.columns)

    # Populate the new user's row with the provided ratings
    for movie_id, rating in new_user_ratings.items():
        movie_id = int(movie_id)
        if movie_id in new_user_row.index:
            new_user_row[movie_id] = rating

    # Add new user to the matrix
    user_movie_matrix.loc[new_user_id] = new_user_row

    # Normalize ratings by subtracting the mean rating for each user
    user_ratings_mean = user_movie_matrix.mean(axis=1)
    matrix_norm = user_movie_matrix.sub(user_ratings_mean, axis=0)

    # Perform SVD
    U, sigma, Vt = svds(matrix_norm.values, k=30)

    # Convert diagonal array to matrix
    sigma = np.diag(sigma)

    # Predict ratings using the SVD components
    predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.values.reshape(-1, 1)
    predicted_ratings_df = pd.DataFrame(
        predicted_ratings,
        index=user_movie_matrix.index,
        columns=user_movie_matrix.columns
    )

    # Get the new user's predicted ratings
    new_user_predictions = predicted_ratings_df.loc[new_user_id]

    # Filter out movies the user has already rated
    rated_movies = set(int(movie_id) for movie_id, rating in new_user_ratings.items() if rating > 0)
    unrated_movies = new_user_predictions[~new_user_predictions.index.isin(rated_movies)]

    # Calculate popularity scores
    popularity_scores = ratings.groupby('movieId')['rating'].agg(['count', 'mean']).reset_index()
    popularity_scores['score'] = popularity_scores['count'] * popularity_scores['mean']
    popularity_dict = popularity_scores.set_index('movieId')['score'].to_dict()

    # Calculate final scores
    final_scores = unrated_movies.map(lambda x: x / (1 + np.log(1 + popularity_dict.get(x, 0))))

    # Return top N recommendations
    recommendations = final_scores.sort_values(ascending=False).head(top_n)

    return recommendations

def get_recommendations(items, top_n=3):
    recommendations = get_recommendation_items(items, top_n)
    return [{"movieLensId": str(movie_id), "pred_score": score} for movie_id, score in recommendations.items()]