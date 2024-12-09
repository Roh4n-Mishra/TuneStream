import pymongo
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["music_recommendation"]
artists_collection = db["artists"]


def load_artists_data():
    """Fetch all artist data from MongoDB and return as a DataFrame."""
    artists = list(artists_collection.find({}, {"_id": 0, "name": 1, "genre": 1, "popularity": 1, "songs": 1}))
    return pd.DataFrame(artists)


def preprocess_data(df):
    """Preprocess artist data by converting categorical genres to one-hot encoding."""
    genre_onehot = pd.get_dummies(df['genre'])  
    df_processed = pd.concat([df[['name', 'popularity', 'songs']], genre_onehot], axis=1)
    return df_processed


def recommend_artists(user_input, df_processed, top_n=5):
    """
    Recommend similar artists based on user preferences using cosine similarity.
    :param user_input: List of preferred artist names.
    :param df_processed: Preprocessed DataFrame with artist features.
    :param top_n: Number of recommendations to return.
    """
    
    user_artists = df_processed[df_processed['name'].isin(user_input)]
    
    if user_artists.empty:
        return f"None of the artists in the user's input were found."
    
    user_features = user_artists.drop(['name', 'songs'], axis=1).mean().values.reshape(1, -1)
    
    
    artist_features = df_processed.drop(['name', 'songs'], axis=1).values
    similarity = cosine_similarity(user_features, artist_features).flatten()
    
    
    similar_indices = similarity.argsort()[::-1]
    recommended_artists = df_processed.iloc[similar_indices].head(top_n)
    
    recommendations = []
    for idx, row in recommended_artists.iterrows():
        recommendations.append({
            'name': row['name'],
            'popularity': row['popularity'],
            'songs': row['songs']
        })
    
    return recommendations


def get_recommendations(user_preferences):
    """
    Main function to process data and get artist/song recommendations.
    :param user_preferences: List of user-preferred artist names.
    :return: List of recommended artists and songs.
    """
    
    df = load_artists_data()
    
    
    df_processed = preprocess_data(df)
    
    
    recommendations = recommend_artists(user_preferences, df_processed)
    
    return recommendations


if __name__ == "__main__":
    
    user_preferences = ["Taylor Swift", "A. R. Rahman", "Ed Sheeran"]
    
    
    recommendations = get_recommendations(user_preferences)
    
    
    print("Recommended Artists and Songs:")
    for rec in recommendations:
        print(f"Artist: {rec['name']}, Popularity: {rec['popularity']}")
        print("Songs: ", ", ".join(rec['songs']))
        print("\n")
