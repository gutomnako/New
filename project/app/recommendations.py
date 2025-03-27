
from django.db.models import Count
from .models import Resort, Favorite

def get_recommendations(user_id, n_recommendations=5):
    
    user_favorites = set(Favorite.objects.filter(user_id=user_id).values_list('resort_id', flat=True))

    similar_users = Favorite.objects.filter(resort_id__in=user_favorites).exclude(user_id=user_id)
    similar_users_ids = similar_users.values_list('user_id', flat=True)

    resort_like_counts = Favorite.objects.filter(user_id__in=similar_users_ids)\
        .exclude(resort_id__in=user_favorites)\
        .values('resort_id')\
        .annotate(like_count=Count('resort_id'))

    like_scores = {resort['resort_id']: resort['like_count'] for resort in resort_like_counts}

    top_recommendations = sorted(like_scores, key=like_scores.get, reverse=True)[:n_recommendations]
    recommended_resorts = Resort.objects.filter(id__in=top_recommendations)

    return recommended_resorts
