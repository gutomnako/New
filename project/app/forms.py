from django.forms import ModelForm
from .models import Resort, User
from django.contrib.auth.forms import UserCreationForm


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model =User
        fields =  ['username', 'password1', 'password2']


class ResortForm(ModelForm):
    class Meta:
        model = Resort
        fields = [
            'host', 'name', 'location', 'description', 
            'amenities', 'price_per_night', 
            'entrance_kids', 'entrance_adults', 
            'contact_number', 'resort_image', 'price'
            ]
        


class Userform(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']