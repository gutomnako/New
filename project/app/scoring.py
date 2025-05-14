from django.db.models import Count, Min, Max, F, FloatField, ExpressionWrapper, Value, Case, When, DecimalField, Avg
from app.models import Resort, Rating

def get_ranked_resorts(resorts, weights):
    # Annotate each resort with rating stats, amenities, and computed total price
    resorts = resorts.annotate(
        # Average rating and total ratings count
        average_rating=Avg('rating__rating'),
        rating_count=Count('rating', distinct=True),
        # Total amenities count (assuming 'amenities' is a ManyToManyField or related model)
        amenity_count=Count('amenities', distinct=True),
        # Total price calculation
        computed_total_price=(
            F('price') + F('entrance_kids') + F('entrance_adults') +
            Case(
                When(room_price_range='Low', then=Value(999)),
                When(room_price_range='Average', then=Value(2000)),
                When(room_price_range='High', then=Value(3000)),
                default=Value(0),
                output_field=DecimalField()
            ) +
            Case(
                When(cottage_price_range='Low', then=Value(999)),
                When(cottage_price_range='Average', then=Value(2000)),
                When(cottage_price_range='High', then=Value(3000)),
                default=Value(0),
                output_field=DecimalField()
            )
        )
    )

    # Fetch min/max values for normalization
    min_values = resorts.aggregate(
        min_price=Min('computed_total_price'),
        max_price=Max('computed_total_price'),
        min_rating=Min('average_rating'),
        max_rating=Max('average_rating'),
        min_amenities=Min('amenity_count'),
        max_amenities=Max('amenity_count'),
        min_location=Min('location_rating'),
        max_location=Max('location_rating')
    )

    # Prevent division by zero and handle price prioritization (invert for price)
    def safe_normalization(field, min_val, max_val, invert=False):
        if invert:
            return ExpressionWrapper(
                (Value(1) - (F(field) - Value(min_val)) / (Value(max_val) - Value(min_val))) 
                if min_val != max_val else Value(0),
                output_field=FloatField()
            )
        else:
            return ExpressionWrapper(
                (F(field) - Value(min_val)) / (Value(max_val) - Value(min_val)) 
                if min_val != max_val else Value(0),
                output_field=FloatField()
            )

    # Annotate resorts with normalized values
    resorts = resorts.annotate(
        norm_price=safe_normalization('computed_total_price', min_values['min_price'], min_values['max_price'], invert=True),
        norm_rating=safe_normalization('average_rating', min_values['min_rating'], min_values['max_rating']),
        norm_amenities=safe_normalization('amenity_count', min_values['min_amenities'], min_values['max_amenities']),
        norm_location=safe_normalization('location_rating', min_values['min_location'], min_values['max_location'])
    ).annotate(
        score=ExpressionWrapper(
            weights['price'] * F('norm_price') +
            weights['rank'] * F('norm_rating') +  # Use 'rank' for favorite count here
            weights['location'] * F('norm_location') +
            weights['amenities'] * F('norm_amenities'),
            output_field=FloatField()
        )
    ).order_by('-score')

    return resorts
