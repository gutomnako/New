# app/recommendations.py
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
import pandas as pd
from collections import defaultdict
from django.db.models import Count
from .models import Resort, Rating, Favorite

def get_recommendations(user_id, n_recommendations=5):
    # Step 1: Get resorts the user has rated
    user_ratings = set(Rating.objects.filter(user_id=user_id).values_list('resort_id', flat=True))

    # Step 2: Get resorts the user has favorited (liked)
    user_favorites = set(Favorite.objects.filter(user_id=user_id).values_list('resort_id', flat=True))

    # Step 3: Find similar users based on favorites
    similar_users = Favorite.objects.filter(resort_id__in=user_favorites).exclude(user_id=user_id)
    similar_users_ids = similar_users.values_list('user_id', flat=True)

    # Step 4: Count how many times each resort is liked by similar users
    resort_like_counts = Favorite.objects.filter(user_id__in=similar_users_ids)\
        .exclude(resort_id__in=user_favorites)\
        .values('resort_id')\
        .annotate(like_count=Count('resort_id'))

    # Convert to dictionary: {resort_id: like_count}
    like_scores = {resort['resort_id']: resort['like_count'] for resort in resort_like_counts}

    # Step 5: Collaborative Filtering (Rating-Based Recommendations)
    all_resorts = Resort.objects.exclude(id__in=user_ratings)  # Exclude already rated resorts

    ratings_data = Rating.objects.all().values('user_id', 'resort_id', 'rating')
    df = pd.DataFrame(ratings_data)

    predicted_ratings = {}

    if not df.empty:
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[['user_id', 'resort_id', 'rating']], reader)
        trainset, _ = train_test_split(data, test_size=0.2)
        model = KNNBasic(sim_options={'name': 'cosine', 'user_based': False})
        model.fit(trainset)

        # Predict ratings for unrated resorts
        predicted_ratings = {resort.id: model.predict(user_id, resort.id).est for resort in all_resorts}

    # Step 6: Combine Ratings and Like Scores
    final_scores = defaultdict(float)

    for resort in all_resorts:
        like_score = like_scores.get(resort.id, 0)  # Default to 0 if not found
        rating_score = predicted_ratings.get(resort.id, 0)  # Default to 0 if not predicted

        # Weighted combination (Adjust weights as needed)
        final_scores[resort.id] = (0.6 * rating_score) + (0.4 * like_score)

    # Step 7: Sort and get top recommendations
    top_recommendations = sorted(final_scores, key=final_scores.get, reverse=True)[:n_recommendations]
    recommended_resorts = Resort.objects.filter(id__in=top_recommendations)

    return recommended_resorts
