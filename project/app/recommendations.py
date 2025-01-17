# app/recommendations.py
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
import pandas as pd
from .models import Resort, Rating

def get_recommendations(user_id, n_recommendations=5):
    user_ratings = Rating.objects.filter(user_id=user_id)
    all_resorts = Resort.objects.all()

    # Filter out resorts that the user has already rated
    unrated_resorts = [resort for resort in all_resorts if resort.id not in [r.resort_id for r in user_ratings]]

    # Prepare the dataset for collaborative filtering
    ratings_data = Rating.objects.all().values('user_id', 'resort_id', 'rating')
    df = pd.DataFrame(ratings_data)
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user_id', 'resort_id', 'rating']], reader)

    # Train-test split for collaborative filtering
    trainset, testset = train_test_split(data, test_size=0.2)
    model = KNNBasic(sim_options={'name': 'cosine', 'user_based': False})
    model.fit(trainset)

    # Generate predictions for unrated resorts
    predictions = [model.predict(user_id, resort.id) for resort in unrated_resorts]
    predictions.sort(key=lambda x: x.est, reverse=True)
    top_predictions = predictions[:n_recommendations]

    # Debugging: Print out the top recommendations
    print(f"Top recommended resorts for user {user_id}:")
    for prediction in top_predictions:
        print(f"Resort ID: {prediction.iid}, Predicted rating: {prediction.est}")

    # Get the top recommended resorts
    recommended_resorts = [Resort.objects.get(id=prediction.iid) for prediction in top_predictions]

    # Debugging: Print the resort names
    print("Resorts in the recommendation list:")
    for resort in recommended_resorts:
        print(resort.name)

    return recommended_resorts
