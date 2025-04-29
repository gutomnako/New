from django.forms import ModelForm
from .models import Resort, User, Rating, SubAdminApplication
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms
from django.core.validators import RegexValidator

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']  # Only the rating field is needed, as the resort and user are already linked

    rating = forms.IntegerField(
        min_value=1, 
        max_value=5, 
        widget=forms.NumberInput(attrs={'type': 'number', 'step': '1', 'min': '1', 'max': '5'})
    )
 
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    username = forms.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.')],
        error_messages={  # Override error messages for the username field
            'required': '',
            'max_length': '',
            'validators': ''  # This hides the default validation message
        }
    )

    # Override password fields
    password1 = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput, 
        help_text=None  # Hide the default password help text
    )
    
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text=None  # Hide the default confirmation help text
    )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        # Custom password validation logic, if you need to apply any checks
        if password and len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        
        return password2

class ResortForm(ModelForm):
    class Meta:
        model = Resort
        fields = [
            'name', 'location', 'description', 
            'amenities', 'resort_image'
            ]

class SubAdminApplicationForm(forms.ModelForm):
    class Meta:
        model = SubAdminApplication
        fields = ['resort_name', 'location', 'description', 'email', 'phone', 'amenities', 'resort_image']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # If email is empty, raise a validation error
        if not email:
            raise forms.ValidationError("Email is required.")
        
        # Optionally, you can apply .lower() here to ensure the email is case-insensitive before saving
        email = email.lower()
        
        # Return the cleaned and standardized email
        return email       

class Userform(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']

    # Add custom validation for the email field
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email is empty
        if not email:
            raise ValidationError("Email cannot be empty.")
        
        # Check if email is already used
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already taken.")
        
        return email
