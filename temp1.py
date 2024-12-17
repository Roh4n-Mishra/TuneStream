import pymongo
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Music"]
artists_collection = db["Artists"]

def normalize_artist_names():
    """
    Update the MongoDB collection to add a 'normalized_name' field with title case for consistent search.
    """
    for artist in artists_collection.find():
        normalized_name = artist["name"].title() 
        artists_collection.update_one({"_id": artist["_id"]}, {"$set": {"normalized_name": normalized_name}})

def load_artists_data():
    """Fetch all artist data from MongoDB and return as a DataFrame."""
    artists = list(artists_collection.find({}, {"_id": 0, "name": 1, "genre": 1, "popularity": 1, "song": 1, "normalized_name": 1}))
    return pd.DataFrame(artists)

def preprocess_data(df):
    """Preprocess artist data by converting categorical genres to one-hot encoding."""
    genre_onehot = pd.get_dummies(df['genre'])  
    df_processed = pd.concat([df[['name', 'popularity', 'song', 'normalized_name']], genre_onehot], axis=1)
    return df_processed

def recommend_artists(user_input, df_processed, top_n=5):
    """
    Recommend similar artists based on user preferences using cosine similarity.
    :param user_input: List of preferred artist names.
    :param df_processed: Preprocessed DataFrame with artist features.
    :param top_n: Number of recommendations to return.
    """
    
    user_input = [name.title() for name in user_input]
    
    user_artists = df_processed[df_processed['normalized_name'].isin(user_input)]
    
    if user_artists.empty:
        return "None of the artists in the user's input were found."
    
    user_features = user_artists.drop(['name', 'song', 'normalized_name'], axis=1).mean().values.reshape(1, -1)
    artist_features = df_processed.drop(['name', 'song', 'normalized_name'], axis=1).values
    similarity = cosine_similarity(user_features, artist_features).flatten()
    
    similar_indices = similarity.argsort()[::-1]
    recommended_artists = df_processed.iloc[similar_indices].head(top_n)
    
    recommendations = []
    for idx, row in recommended_artists.iterrows():
        recommendations.append({
            'name': row['name'],
            'popularity': row['popularity'],
            'song': row['song']
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

def out(user_input: str) -> str:
    normalize_artist_names()
    user_preferences = [user_input]
    recommendations = get_recommendations(user_preferences)

    if isinstance(recommendations, str):  # If recommendations is an error message
        return f"<p class='error'>{recommendations}</p>"

    output = "<div class='artist-recommendations'>"
    for i,rec in enumerate(recommendations):
        output += f"""
        <div class='artist-entry artist-{i + 1}'>
            <p class='resPara'><strong>Artist:</strong> {rec['name']}</p>
            <p class='resPara'><strong>Popularity:</strong> {rec['popularity']}</p>
            <p class='resPara'><strong>Song:</strong> {rec['song']}</p>
        </div>
        """
    
    output += "</div>"
    return output






