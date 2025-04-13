from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F, Sum, OuterRef, Subquery, Avg, Exists, Value
from django.contrib.auth.decorators import login_required
from .models import Resort, Amenity, Location, Message, User, Favorite, Rating, ResortImage
from django.contrib.auth import authenticate, login, logout
from .forms import ResortForm, MyUserCreationForm, RatingForm
from django.contrib import messages
from django.http import HttpResponse
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group
from django.utils.timezone import now, timedelta
from .models import LoginActivity, LoginHistory, Visit
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from django.http import JsonResponse
import json
from .recommendations import get_recommendations
from app.scoring import get_ranked_resorts
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from decimal import Decimal, InvalidOperation
from django.views.decorators.csrf import csrf_exempt
import re
from collections import Counter
from django.utils import timezone



#dashboard
#login
#resorts
#edit resort
#comments

#dashboard
@login_required
def some_view(request):
    
    cancel_url = 'home'

    if request.user.groups.filter(name='Pinakaadmin').exists():
        cancel_url = 'admin-dashboard'

    return render(request, 'app/adminDashboard.html', {'cancel_url': cancel_url})

@admin_only
def adminDashboard(request):
    resorts = Resort.objects.all()
    login_history = LoginHistory.objects.all().order_by('-last_login')
    unique_users_count = login_history.values('user').distinct().count()

    today = now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    def get_visit_count(resort, start_date):
        return resort.visits.filter(timestamp__gte=start_date).count()

    resort_visit_data = []
    for resort in resorts:
        resort_data = {
            "name": resort.name,
            "daily": get_visit_count(resort, today),
            "weekly": get_visit_count(resort, week_ago),
            "monthly": get_visit_count(resort, month_ago),
            "yearly": get_visit_count(resort, year_ago),
        }
        resort_visit_data.append(resort_data)

    all_messages = Message.objects.select_related('user').order_by('-created_at').annotate(
    rating=Subquery(
        Rating.objects.filter(
            user=OuterRef('user'),
            resort=OuterRef('resort')
        ).values('rating')[:1]  
    )
)

    context = {
        'resorts': resorts,
        'login_history': login_history,
        'unique_users_count': unique_users_count,
        'resort_visit_data': resort_visit_data,
        'all_messages': all_messages,  
    }

    if login_history.exists():
        context['login_activities'] = LoginActivity.objects.filter(user=request.user).order_by('-timestamp')
    else:
        context['error'] = 'No login history found.'

    return render(request, 'app/adminDashboard.html', context)


@admin_only
def adminresorts(request):
      resorts = Resort.objects.all().order_by('-created_at')
     
      return render(request, 'app/beachandresorts.html', {'resorts': resorts})

@admin_only
def adminmonitors(request):
      resorts = Resort.objects.all()
      login_history = LoginHistory.objects.all().order_by('-last_login')

      unique_users_count = login_history.values('user').distinct().count()

      if not login_history:
        return render(request, 'app/recent-logins.html',
            {'error': 'No login history found.',
            'resorts': resorts,
            'login_history': login_history,
            'unique_users_count': unique_users_count, })

      login_activities = LoginActivity.objects.filter(user=request.user).order_by('-timestamp')
      return render(request, 'app/recent-logins.html', {'resorts': resorts, 'login_history': login_history,
            'login_activities': login_activities})
#end dashboard

#login
@unauthenticated_user 
def loginPage(request):
      page = 'login'
      if request.user.is_authenticated:
        return redirect('index-view')
    
      if request.method == 'POST':
            username = request.POST.get('username').lower()
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                  login(request, user)

                  if user.groups.filter(name='pinakaadmin').exists():
                   return redirect('admin-dashboard')
                  
                  return redirect('index-view')
            else:
                  messages.error(request, 'User does not exist OR password is incorrect')
      
      context = {'page': page}
      return render(request, 'app/login_register.html', context)

def logoutUser(request):
      logout(request)
      return redirect('index-view')

@unauthenticated_user
def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)

            group = Group.objects.get(name='users')
            user.groups.add(group)

            return redirect('index-view')
        else:
        
            if 'email' in form.errors:
                messages.error(request, f"Email Error: {form.errors['email'][0]}")
            elif 'username' in form.errors:
                messages.error(request, f"Username Error: {form.errors['username'][0]}")
            else:
                messages.error(request, 'An error occurred during registration')

    return render(request, 'app/login_register.html', {'form': form})
#end login

#resorts
def index_view(request):
  
    resorts = Resort.objects.all()

    rated_resorts = (
        Resort.objects.annotate(average_rating=Avg('rating__rating'))
        .order_by('-average_rating') 
    )

   
    ratings = Rating.objects.all().select_related('user', 'resort')
    data = [{'user': r.user.id, 'resort': r.resort.id, 'rating': r.rating} for r in ratings]

    recommended_resorts = []

    if request.user.is_authenticated and len(data) >= 2:
       
        df = pd.DataFrame(data)
        pivot_table = df.pivot_table(index='user', columns='resort', values='rating').fillna(0)
        similarity_matrix = cosine_similarity(pivot_table)
        user_sim_df = pd.DataFrame(similarity_matrix, index=pivot_table.index, columns=pivot_table.index)
        user_id = request.user.id

        if user_id in user_sim_df.index:
            
            similar_users = user_sim_df[user_id].sort_values(ascending=False).index[1:]
            similar_users_ratings = df[df['user'].isin(similar_users)]
            user_rated_resorts = df[df['user'] == user_id]['resort'].tolist()
            unseen_resorts = similar_users_ratings[~similar_users_ratings['resort'].isin(user_rated_resorts)]
            recommended = (
                unseen_resorts.groupby('resort')['rating']
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )

            
            recommended_resorts = Resort.objects.filter(id__in=recommended['resort'].tolist())

    return render(request, 'app/index_view.html', {
        'resorts': resorts,
        'rated_resorts': rated_resorts, 
        'recommended_resorts': recommended_resorts,  
    })

@login_required
def rate_resort(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)

    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            rating_value = data.get('rating')
            comment_text = data.get('comment')

            if not rating_value:
                return JsonResponse({'success': False, 'message': 'Rating is required.'}, status=400)

            try:
                rating_value = int(rating_value)
                if not (1 <= rating_value <= 5):
                    return JsonResponse({'success': False, 'message': 'Rating must be between 1 and 5.'}, status=400)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid rating value.'}, status=400)

            # Save rating (create or update)
            existing_rating = Rating.objects.filter(user=request.user, resort=resort).first()
            if existing_rating:
                existing_rating.rating = rating_value
                existing_rating.save()
            else:
                Rating.objects.create(user=request.user, resort=resort, rating=rating_value)

            # Save comment if provided
            if comment_text:
                Message.objects.create(user=request.user, resort=resort, comment=comment_text)

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        resort_id = data['resort_id']
        is_favorite = data['is_favorite']

        resort = Resort.objects.get(id=resort_id)
        user = request.user

        if is_favorite:
            Favorite.objects.get_or_create(user=user, resort=resort)
        else:
            Favorite.objects.filter(user=user, resort=resort).delete()

        # Update favorite count for the resort
        updated_favorite_count = Resort.objects.annotate(favorite_count=Count('favorite_resorts'))\
            .get(id=resort_id).favorite_count

        # **Get updated recommendations for the user**
        recommended_resorts = get_recommendations(user.id, n_recommendations=5)

        # Convert recommendations to JSON-friendly format
        recommended_resorts_list = [{'id': resort.id, 'name': resort.name} for resort in recommended_resorts]

        return JsonResponse({
            'status': 'success',
            'favorite_count': updated_favorite_count,
            'recommended_resorts': recommended_resorts_list  # Include recommended resorts
        })
    
    return JsonResponse({'status': 'failed'}, status=400)

def autocomplete(request):
    query = request.GET.get('q', '').lower()
    suggestions = []

    if query:
        resorts = Resort.objects.all()
        for resort in resorts:
            # Combine all text to search through
            text = f"{resort.name} {resort.description or ''} {' '.join(resort.amenities.values_list('name', flat=True))}"
            words = re.findall(r'\b\w+\b', text.lower())  # Split text into words

            # Match query and gather two-word suggestions
            for i, word in enumerate(words[:-1]):  # Loop through all words except the last one
                if word.startswith(query):  # Match based on the query starting the word
                    next_word = words[i + 1]  # Get the next word as suggestion
                    suggestion = f"{word} {next_word}"  # Combine word and next word
                    suggestions.append(suggestion)  # Add to list

    return JsonResponse({'suggestions': suggestions[:5]})  # Limit to 5 suggestions


def home(request):
    q = request.GET.get('q', '').strip()

    if q:
        resorts = Resort.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(amenities__name__icontains=q)
        ).distinct().order_by('-created_at')
    else:
        resorts = Resort.objects.all().order_by('-created_at')

    # Get filter parameters
    selected_amenities = request.GET.getlist('amenities')  
    selected_location = request.GET.getlist('location')   
    min_price = request.GET.get('min_price') 
    max_price = request.GET.get('max_price')  

    # Apply filters
    if selected_amenities:
        resorts = resorts.filter(amenities__id__in=selected_amenities).distinct()

    if selected_location:
        resorts = resorts.filter(location__id__in=selected_location).distinct()

    # Ensure proper price filtering
    try:
        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None
    except ValueError:
        min_price = None
        max_price = None

    if min_price is not None or max_price is not None:
        resorts = resorts.annotate(
            total_price=F('price_per_night') + F('entrance_kids') + F('entrance_adults')
        )
        if min_price is not None:
            resorts = resorts.filter(total_price__gte=min_price)
        if max_price is not None:
            resorts = resorts.filter(total_price__lte=max_price)

    # Annotate resorts with favorite count
    resorts = resorts.annotate(
        favorite_count=Count('favorite_resorts', distinct=True),
        is_favorite=Exists(
            Favorite.objects.filter(user=request.user, resort=OuterRef('pk'))
        ) if request.user.is_authenticated else Value(False)
    )
    resorts = get_ranked_resorts(resorts)

    # Apply ranking for rated resorts (by average rating)
    rated_resorts = Resort.objects.annotate(
        average_rating=Avg('rating__rating'),
        favorite_count=Count('favorite_resorts', distinct=True)  # Add favorite count
    ).order_by('-average_rating')  


    user = request.user
    recommendations = []

    # Fetch recommendations for authenticated users
    if user.is_authenticated:
        recommendations = get_recommendations(user.id, n_recommendations=5)

        # Get recommended resort IDs
        recommendation_ids = [resort.id for resort in recommendations]

        # Fetch resorts with favorite count and order by most favorited
        annotated_recommendations = (
            Resort.objects.filter(id__in=recommendation_ids)
            .annotate(favorite_count=Count('favorite_resorts', distinct=True))
            .order_by('-favorite_count')  # Order by highest favorite count
        )

        # Map favorite count and is_favorite back to recommendations
        for resort in annotated_recommendations:
            resort.is_favorite = Favorite.objects.filter(user=user, resort=resort).exists()

        # Assign sorted recommendations back
        recommendations = list(annotated_recommendations)

    # Add `is_favorite` to all rated resorts
    for resort in rated_resorts:  
        resort.is_favorite = user.is_authenticated and Favorite.objects.filter(user=user, resort=resort).exists()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        resorts_data = list(resorts.values(
            'id', 'name', 'description', 'entrance_kids', 'entrance_adults', 'price_per_night', 'resort_image', 'score'
        ))

        for resort in resorts_data:
            resort['total_price'] = float(resort['price_per_night']) + float(resort['entrance_kids']) + float(resort['entrance_adults'])

            # Ensure image URLs are correct
            if resort['resort_image']:
                resort['resort_image'] = f"/media/{resort['resort_image']}"

            resort['is_favorite'] = Favorite.objects.filter(user=user, resort_id=resort['id']).exists() if user.is_authenticated else False  
            resort['favorite_count'] = Favorite.objects.filter(resort_id=resort['id']).count()

        return JsonResponse({
            'resorts': resorts_data,
            'selected_amenities': selected_amenities,
            'selected_location': selected_location,
            'min_price': min_price,
            'max_price': max_price,
        })

    amenities = Amenity.objects.all()
    locations = Location.objects.all()
    resort_count = rated_resorts.count()  # Get the count of rated resorts  

    context = {
        'resorts': resorts,  # Resorts ordered by creation date
        'recommendations': recommendations,  # Ordered by favorite count
        'amenities': amenities,
        'resort_count': resort_count,
        'locations': locations,
        'selected_amenities': selected_amenities,
        'selected_location': selected_location,
        'min_price': min_price,
        'max_price': max_price,
        "rated_resorts": rated_resorts,  # Resorts ordered by average rating
        "show_scores": True,
        'q': q
    }

    return render(request, 'app/home.html', context)

@login_required
def update_resort(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)

    if request.method == "POST":
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            field_map = {
                "mini_description": "mini_description",
                "description": "description",
                "price_per_night": "price_per_night",
                "entrance_kids": "entrance_kids",
                "entrance_adults": "entrance_adults",
                "cottage": "cottage",
                "price": "price",
                "room_description": "room_description",
                "beach_description": "beach_description",
                "activity_description": "activity_description",
            }

            for field, model_field in field_map.items():
                if field in request.POST:
                    setattr(resort, model_field, request.POST[field])

            resort.save()
            return JsonResponse({"success": True})

        # Update text fields
        resort.mini_description = request.POST.get("mini_description", resort.mini_description)
        resort.description = request.POST.get("description", resort.description)
        resort.price_per_night = request.POST.get("price_per_night", resort.price_per_night)
        resort.entrance_kids = request.POST.get("entrance_kids", resort.entrance_kids)
        resort.entrance_adults = request.POST.get("entrance_adults", resort.entrance_adults)
        resort.cottage = request.POST.get("cottage", resort.cottage)
        resort.price = request.POST.get("price", resort.price)
        resort.room_description = request.POST.get("room_description", resort.room_description)
        resort.beach_description = request.POST.get("beach_description", resort.beach_description)  # Fixed
        resort.activity_description = request.POST.get("activity_description", resort.activity_description)  # Fixed

        # Handle image uploads
        if 'hero_image' in request.FILES:
            resort.hero_image = request.FILES['hero_image']
        if 'resort_image' in request.FILES:
            resort.resort_image = request.FILES['resort_image']
        if 'roomimage' in request.FILES:
            resort.roomimage = request.FILES['roomimage']
        if 'beachimage' in request.FILES:
            resort.beachimage = request.FILES['beachimage']
        if 'activities_image' in request.FILES:
            resort.activities_image = request.FILES['activities_image']

        # Handle amenities
        amenity_names = request.POST.getlist("amenities")
        for name in amenity_names:
            if name.strip():
                amenity, created = Amenity.objects.get_or_create(name=name.strip())
                resort.amenities.add(amenity)

        new_amenity = request.POST.get("new_amenity")
        if new_amenity:
            new_amenity_obj, created = Amenity.objects.get_or_create(name=new_amenity.strip())
            resort.amenities.add(new_amenity_obj)

             # Handle comments
        if "comment" in request.POST:
            comment_text = request.POST.get("comment", "").strip()  # Strip spaces
            if comment_text:  # Check if the comment is not empty
                Message.objects.create(
                    user=request.user,
                    resort=resort,
                    comment=comment_text
                )

        resort.save()
        messages.success(request, "Resort details updated successfully!")
        return redirect("resort", pk=resort.id)

    return redirect("resort", pk=resort.id)

def resort_detail(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)

    # Record the visit (example logic — you may adapt)
    Visit.objects.create(user=request.user, resort=resort, date=timezone.now().date())

    return render(request, 'resort_detail.html', {
        'resort': resort,
        # other context
    })

@csrf_exempt
def resort(request, pk):
    resort = Resort.objects.get(id=pk)
    amenities = Amenity.objects.all()
    resort_messages = resort.messages.all().order_by('-created_at')

    if request.user.is_authenticated:
        Visit.objects.create(resort=resort, user=request.user)

    average_rating = Rating.objects.filter(resort=resort).aggregate(Avg('rating'))['rating__avg']

    # Handle AJAX updates
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            field = data.get('field')  # Example: 'description', 'price_per_night', etc.
            value = data.get('value')

            if field in ['description', 'mini_description', 'price_per_night', 'entrance_kids', 'entrance_adults', 'cottage', 'price']:
                setattr(resort, field, value)
                resort.save()
                return JsonResponse({'success': True, 'message': 'Updated successfully!'})

            return JsonResponse({'success': False, 'message': 'Invalid field!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    context = {
        'resort': resort,
        'resort_messages': resort_messages,
        'amenities': amenities,
        'average_rating': average_rating,
    }
    return render(request, 'app/resort.html', context)

def map_view(request):
    resorts = Resort.objects.all()
    context = {'resorts': resorts}
    return render(request, 'app/map.html', context)

def contact_number(request):
      resort = Resort.objects.first()
      contact = resort.contact_number if resort else "No contact number available"
      context = {'contact_number': contact}
      return render(request, 'app/contact_number.html', context)


def userProfile(request, pk):
    user = get_object_or_404(User, id=pk)  # Get user by ID or return 404
    favorites = Favorite.objects.filter(user=user)  # Get user's favorite resorts
    messages = Message.objects.filter(user=user)  # Get user's messages/comments
    ratings = Rating.objects.filter(user=user)  # Get user's ratings

    context = {
        'user': user,
        'favorites': favorites,
        'messages': messages,
        'ratings': ratings,  
    }
    return render(request, 'app/profile.html', context)

#end resorts

#edit resort
@login_required(login_url='login')
@allowed_users(allowed_roles=['Pinakaadmin'])
def createResort(request):
      form = ResortForm()
      
      if request.method == 'POST':
            form = ResortForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect ('home')
      context = {'form': form}
      return render(request, 'app/resort_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['subadmin'])
def updateResort(request, pk):
      resort = Resort.objects.get(id=pk)
      form = ResortForm(instance=resort)

      if request.user != resort.host:
            return HttpResponse('You are not allowed here!')

      if request.method =="POST":
            form = ResortForm(request.POST, request.FILES, instance=resort)
            if form.is_valid():
                  form.save()
                  return redirect('home')
      else:
        form = ResortForm(instance=resort)
            
      context = {'form': form}
      return render(request, 'app/resort_form.html', context)

@login_required
#def update_resort(request, resort_id):
#    resort = get_object_or_404(Resort, id=resort_id)

 #   if request.user != resort.host:
   #     return redirect("resort-detail", resort_id=resort.id)

  #  if request.method == "POST":
  #      new_description = request.POST.get("description")
   #     if new_description:  # Ensure it's not empty
    #        resort.description = new_description
   #         resort.save()
    #    return redirect("resort-detail", resort_id=resort.id)

   # return render(request, "resort_detail.html", {"resort": resort})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Pinakaadmin'])
def deleteResort(request, pk):
      resort = Resort.objects.get(id=pk)
      if request.method == 'POST':
            resort.delete()
            return redirect('home')
      return render(request, 'app/delete.html', {'obj': resort})

@login_required
@csrf_exempt
def update_resort_inline(request, resort_id):
    if request.method == "POST":
        resort = Resort.objects.get(id=resort_id)

        # Ensure only the host can edit
        if request.user != resort.host:
            return JsonResponse({"success": False, "error": "❌ Unauthorized!"})

        try:
            data = json.loads(request.body)
            field = data.get("field")
            value = data.get("value")

            if field == "description":
                resort.description = value
                resort.save()
                return JsonResponse({"success": True, "message": "✅ Description updated successfully!"})

            return JsonResponse({"success": False, "error": "❌ Invalid field provided!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "❌ Invalid request!"})

@login_required
def update_resort_images(request, pk):
    resort = Resort.objects.get(id=pk)

    # Check if the user is authorized
    if request.user != resort.host:
        return JsonResponse({'error': 'You are not allowed to edit this resort'}, status=403)

    if request.method == "POST":
        updated_images = {}

        # Handle hero image upload
        if 'hero_image' in request.FILES:
            resort.hero_image = request.FILES['hero_image']
            updated_images["hero_image_url"] = resort.hero_image.url

        # Handle room images
        if 'roomimage' in request.FILES:
            resort.roomimage = request.FILES['roomimage']
            updated_images["roomimage_url"] = resort.roomimage.url

        # Handle beach image upload
        if 'beachimage' in request.FILES:
            resort.beachimage = request.FILES['beachimage']
            updated_images["beachimage_url"] = resort.beachimage.url

        if 'activities_image' in request.FILES:
            resort.activities_image = request.FILES['activities_image']
            updated_images["activities_image_url"] = resort.activities_image.url

        if updated_images:
            resort.save()
            return JsonResponse({"status": "success", "updated_images": updated_images})

    return JsonResponse({"error": "Invalid request method or missing file"}, status=400)
#end edit

#comments
@login_required(login_url='login')
def deleteMessage(request, pk):
      message = Message.objects.get(id=pk)

      if request.user != message.user:
            return HttpResponse ('You are not allowed here!')

      if request.method == 'POST':
            message.delete()
            return redirect('home')
      return render(request, 'app/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
      return render(request, 'app/update-user.html')

def ranked_resorts_view(request):
    resorts = Resort.objects.get_ranked_resorts()
    return render(request, 'resorts/ranked_list.html', {'resorts': resorts})
#end comments

