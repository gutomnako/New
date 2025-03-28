from django.db.models import Count, Min, Max, F, FloatField, ExpressionWrapper, Value
from app.models import Resort

def get_ranked_resorts(resorts):
    # First, annotate each resort with the count of favorites and amenities
    resorts = resorts.annotate(
        favorite_count=Count('favorites', distinct=True),
        amenity_count=Count('amenities', distinct=True)
    )

    # Fetch min/max values for normalization
    min_values = resorts.aggregate(
        min_price=Min('price_per_night'),
        max_price=Max('price_per_night'),
        min_rank=Min('favorite_count'),
        max_rank=Max('favorite_count'),
        min_amenities=Min('amenity_count'),
        max_amenities=Max('amenity_count'),
        min_location=Min('location_rating'),
        max_location=Max('location_rating')
    )

    # Define weights
    weights = {
        'price': 0.4,
        'rank': 0.35,
        'location': 0.15,
        'amenities': 0.1
    }

    # Prevent division by zero
    def safe_normalization(field, min_val, max_val):
        return ExpressionWrapper(
            (F(field) - Value(min_val)) / (Value(max_val) - Value(min_val)) if min_val != max_val else Value(0),
            output_field=FloatField()
        )

    # Annotate resorts with normalized values
    resorts = resorts.annotate(
        norm_price=safe_normalization('price_per_night', min_values['min_price'], min_values['max_price']),
        norm_rank=safe_normalization('favorite_count', min_values['min_rank'], min_values['max_rank']),
        norm_amenities=safe_normalization('amenity_count', min_values['min_amenities'], min_values['max_amenities']),
        norm_location=safe_normalization('location_rating', min_values['min_location'], min_values['max_location'])
    ).annotate(
        score=ExpressionWrapper(
            weights['price'] * F('norm_price') +
            weights['rank'] * F('norm_rank') +
            weights['location'] * F('norm_location') +
            weights['amenities'] * F('norm_amenities'),
            output_field=FloatField()
        )
    ).order_by('-score')

    return resorts



