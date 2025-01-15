from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Resort, Amenity, Location, Message, User, Rating
from django.contrib.auth import authenticate, login, logout
from .forms import ResortForm, MyUserCreationForm, RatingForm
from django.contrib import messages
from django.http import HttpResponse
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group
from .models import LoginActivity, LoginHistory
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Avg
from django.http import JsonResponse

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

      if login_history.exists():  # Check if there is any login history
        login_activities = LoginActivity.objects.filter(user=request.user).order_by('-timestamp')
        return render(request, 'app/adminDashboard.html', {
            'resorts': resorts,
            'login_history': login_history,
            'login_activities': login_activities,
            'unique_users_count': unique_users_count,  # Pass the count to the template
        })
      else:
        return render(request, 'app/adminDashboard.html', {
            'error': 'No login history found.',
            'resorts': resorts,
            'login_history': login_history,
            'unique_users_count': unique_users_count,  # Pass the count even if no history
      })

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

            # Assign user to the default group 'users'
            group = Group.objects.get(name='users')
            user.groups.add(group)

            return redirect('index-view')
        else:
            # Customize error messages based on specific form errors
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
    # Fetch all resorts
    resorts = Resort.objects.all()

    # Calculate the average rating for each resort
    rated_resorts = (
        Resort.objects.annotate(average_rating=Avg('rating__rating'))
        .order_by('-average_rating')  # Sort by the highest average rating
    )

    # Collaborative filtering for recommendations
    ratings = Rating.objects.all().select_related('user', 'resort')
    data = [{'user': r.user.id, 'resort': r.resort.id, 'rating': r.rating} for r in ratings]

    recommended_resorts = []

    if request.user.is_authenticated and len(data) >= 2:
        # Code for collaborative filtering
        df = pd.DataFrame(data)
        
        # Reset the index to avoid alignment issues
        df = df.reset_index(drop=True)  # Reset index of df

        pivot_table = df.pivot_table(index='user', columns='resort', values='rating').fillna(0)
        similarity_matrix = cosine_similarity(pivot_table)
        
        # Reset index of similarity matrix dataframe
        user_sim_df = pd.DataFrame(similarity_matrix, index=pivot_table.index, columns=pivot_table.index)
        user_sim_df = user_sim_df.reset_index(drop=True)  # Reset index of user_sim_df

        user_id = request.user.id
        if user_id in user_sim_df.index:
            similar_users = user_sim_df[user_id].sort_values(ascending=False).index[1:]  # Exclude self
            similar_users_ratings = df[df['user'].isin(similar_users)]
            unseen_resorts = ~df[df['user'] == user_id]['resort'].isin(similar_users_ratings['resort'])
            recommended = (
                similar_users_ratings[unseen_resorts]
                .groupby('resort')['rating']
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            recommended_resorts = Resort.objects.filter(id__in=recommended['resort'].tolist())

    # Debugging: Print out the recommended resorts
    print("Recommended Resorts:", recommended_resorts)

    return render(request, 'app/index_view.html', {
        'resorts': resorts,
        'rated_resorts': rated_resorts,  # This will contain resorts sorted by the highest average rating
        'recommended_resorts': recommended_resorts,  # Collaborative filtering recommendations
    })

@login_required
def rate_resort(request, resort_id):
    if request.method == 'POST':
        resort = get_object_or_404(Resort, id=resort_id)
        rating_value = request.POST.get('rating')

        # Check if the rating is missing
        if not rating_value:
            return HttpResponse("Rating value is required.", status=400)

        # Validate the rating value
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                return HttpResponse("Rating must be between 1 and 5.", status=400)
        except ValueError:
            return HttpResponse("Invalid rating value.", status=400)

        # Handle rating (create or update)
        existing_rating = Rating.objects.filter(user=request.user, resort=resort).first()
        if existing_rating:
            existing_rating.rating = rating_value
            existing_rating.save()
        else:
            Rating.objects.create(user=request.user, resort=resort, rating=rating_value)

        return redirect('home')  # Redirect after rating

    return render(request, 'app/resort_component.html')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''


    resorts = Resort.objects.filter(
        Q(amenities__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(location__name__icontains=q)
        ).distinct()
    
    
    amenities = Amenity.objects.all()
    locations = Location.objects.all()
    resort_count = resorts.count()

    context = {'resorts': resorts, 'amenities': amenities, 'resort_count': resort_count, 'locations': locations}
    return render(request, 'app/home.html', context)


def resort(request, pk):
        resort = Resort.objects.get(id=pk)
        amenities = Amenity.objects.all()
        resort_messages = resort.messages.all().order_by('-created_at')

        if request.method == 'POST':
            message = Message.objects.create(
                  user=request.user,
                  resort=resort,
                  comment=request.POST.get('comment')
            )
            return redirect('resort', pk=resort.id)

        context = {'resort': resort, 'resort_messages': resort_messages, 'amenities': amenities}
        return render(request, 'app/resort.html', context)

def contact_number(request):
      resort = Resort.objects.first()  # Adjust this to filter for the specific entry
      contact = resort.contact_number if resort else "No contact number available"
      context = {'contact_number': contact}
      return render(request, 'app/contact_number.html', context)

def userProfile(request, pk):
      user = User.objects.get(id=pk)
      context = {'user': user}
      return render(request, 'app/profile.html', context) 


def filter_beaches(request):
    selected_amenities = request.GET.getlist('amenities')  
    selected_location = request.GET.getlist('location')   
    
    resorts = Resort.objects.all()

    if selected_amenities:
        resorts = resorts.filter(amenities__id__in=selected_amenities).distinct()

    if selected_location:
        resorts = resorts.filter(location__id__in=selected_location).distinct()

    amenities = Amenity.objects.all()
    locations = Location.objects.all()

    context = {
        'amenities': amenities,
        'selected_amenities': selected_amenities,
        'locations': locations,
        'selected_location': selected_location,
        'resorts': resorts,
    }

    return render(request, 'app/home.html', context)
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['Pinakaadmin'])
def deleteResort(request, pk):
      resort = Resort.objects.get(id=pk)
      if request.method == 'POST':
            resort.delete()
            return redirect('home')
      return render(request, 'app/delete.html', {'obj': resort})
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
      return render(request, 'app/updtae-user.html')
#end comments
