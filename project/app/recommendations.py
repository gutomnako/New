from django.db.models import Count
from .models import Resort, Favorite

def get_recommendations(user_id, n_recommendations=5):
    # Step 1: Get resorts the current user has liked
    user_favorites = set(Favorite.objects.filter(user_id=user_id).values_list('resort_id', flat=True))

    if not user_favorites:
        return Resort.objects.none()

    # Step 2: Find other users who share likes with the current user
    similar_users = Favorite.objects.filter(resort_id__in=user_favorites).exclude(user_id=user_id)

    # Count how many favorites each user shares with the current user
    similar_user_overlap = (
        similar_users
        .values('user_id')
        .annotate(overlap=Count('resort_id'))
        .order_by('-overlap')
    )

    # Create a mapping of user_id -> overlap score
    user_overlap_map = {item['user_id']: item['overlap'] for item in similar_user_overlap}

    if not user_overlap_map:
        return Resort.objects.none()

    # Step 3: For each similar user, get the resorts they liked that the current user hasn’t
    recommendations = Favorite.objects.filter(
        user_id__in=user_overlap_map.keys()
    ).exclude(
        resort_id__in=user_favorites
    ).values('resort_id', 'user_id')

    # Step 4: Score each resort by summing up the overlap score of the users who liked it
    resort_scores = {}
    for rec in recommendations:
        resort_id = rec['resort_id']
        user_score = user_overlap_map[rec['user_id']]
        resort_scores[resort_id] = resort_scores.get(resort_id, 0) + user_score

    # Step 5: Sort and return top N recommended resorts
    top_resort_ids = sorted(resort_scores, key=resort_scores.get, reverse=True)[:n_recommendations]

    # Preserve order
    from django.db.models import Case, When
    preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(top_resort_ids)])
    recommended_resorts = Resort.objects.filter(id__in=top_resort_ids).order_by(preserved_order)

    return recommended_resorts
