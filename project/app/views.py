from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Resort, Amenity, Location, Message
from django.contrib.auth import authenticate, login, logout
from .forms import ResortForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group

#resorts = [
#    {'id':1, 'name':'Del hamor'},
##    {'id':1, 'name':"Zeah's Beach Place"},
#    {'id':1, 'name':'FMB Beach Resort'},
#]


@admin_only
def adminDashboard(request):
      resorts = Resort.objects.all()
      return render(request, 'app/adminDashboard.html', {'resorts': resorts})

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

                  # Redirect Pinakaadmin users to the dashboard
                  if user.groups.filter(name='pinakaadmin').exists():
                   return redirect('admin-dashboard')
                  
                  # Redirect other users to the index view
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
      form = UserCreationForm()

      if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                  user = form.save(commit=False)
                  user.username = user.username.lower()
                  user.save()
                  login(request, user)

                  group = Group.objects.get(name='users')
                  user.groups.add(group)

                  return redirect('index-view')
            else: 
                  messages.error(request, 'An error occured during registration')
            
      return render(request, 'app/login_register.html', {'form': form})

def index_view(request):
    resorts = Resort.objects.all()
    return render(request, 'app/index_view.html', {'resorts': resorts})


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

@login_required(login_url='login')
@allowed_users(allowed_roles=['Pinakaadmin'])
def createResort(request):
      form = ResortForm()
      if request.method == 'POST':
            form = ResortForm(request.POST)
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
            form = ResortForm(request.POST, instance=resort)
            if form.is_valid():
                  form.save()
                  return redirect('home')
            
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

#def filter_beaches(request):
      selected_amenities = request.GET.getlist('amenities')  # Get selected amenities from the request
      selected_location = request.GET.getlist('location')

      #     selected_amenities = [amenity for amenity in selected_amenities if amenity.strip().isdigit()]
      if selected_amenities:
            resorts = Resort.objects.filter(amenities__id__in=selected_amenities).distinct()  # Ensure no duplicates
      else:
            resorts = Resort.objects.all()

      if selected_location:
            location = Resort.objects.filter(location__id__in=selected_location).distinct()
      else:
            location = Resort.objects.all()

      amenities = Amenity.objects.all()  # For rendering checkboxes
      locations = Location.objects.all()   

      context = {
            'amenities': amenities,
            'selected_amenities': selected_amenities,
            'resorts': resorts,
            'selected_location': selected_location,
            'location': location,
            'locations': locations}
      
      return render(request, 'app/home.html', context)

def filter_beaches(request):
    selected_amenities = request.GET.getlist('amenities')  # Get selected amenities
    selected_location = request.GET.getlist('location')   # Get selected locations

    # Start with all resorts
    resorts = Resort.objects.all()

    # Filter by selected amenities
    if selected_amenities:
        resorts = resorts.filter(amenities__id__in=selected_amenities).distinct()

    # Filter by selected locations
    if selected_location:
        resorts = resorts.filter(location__id__in=selected_location).distinct()

    # Fetch all amenities and locations for rendering
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

