from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User

class LoginActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=[('login', 'Login'), ('logout', 'Logout')])
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

# Model to track aggregated login statistics
class LoginHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_logins = models.PositiveIntegerField(default=0)
    total_logouts = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Total Logins: {self.total_logins}, Last Login: {self.last_login}, Last Logout: {self.last_logout}"
    
class User(AbstractUser):
     name = models.CharField(max_length=200, null=True)
     email = models.EmailField(unique=True, null=True, blank=False)
     bio = models.TextField(null=True)
     avatar = models.ImageField(null=True, default="avatar-default.svg")

     USERNAME_FIELD = 'username'
     REQUIRED_FIELDS = []

def validate_non_negative(value):
     if value < 0:
         raise ValidationError("Value must be non-negative.")


class Location(models.Model):
     name = models.CharField(max_length=255, help_text="Name of the location")
    
     def __str__(self):
         return self.name


class Amenity(models.Model):
     name = models.CharField(max_length=255, help_text="Name of the amenity")
        

     def __str__(self):
         return self.name
     
class Resort(models.Model):
     host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
     name = models.CharField(max_length=255, help_text="Name of the resort")
     # message =
     location = models.ManyToManyField(Location, blank=True, related_name="resorts", help_text="Location of the resort")
     description = models.TextField(help_text="Brief description of the resort", blank=True, null=True)
     amenities = models.ManyToManyField(Amenity, blank=True, related_name="resorts", help_text="Amenities available at the resort")
     favorites = models.ManyToManyField(User, through='Favorite', related_name='favorite_resorts')
     price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
     entrance_kids = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative], default=0.00)
     entrance_adults = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative], default=0.00)
     cottage = models.CharField(max_length=100, default="Default Cottage Name")  # Example field
     price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
     contact_number = models.CharField(max_length=20, help_text="Contact phone number")
     resort_image = models.ImageField(upload_to='resorts/', default='paradise.jpg', blank=True, help_text="Image of the resort")
     location_rating = models.FloatField(default=0.0, help_text="A score representing the resort's location")  
     created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the resort was added")
     updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the resort was last updated")
     class Meta:
         ordering =['-updated_at', '-created_at']
    
     def __str__(self):
         return self.name
     
     @property
     def total_price(self):
        """Compute the total price including entrance fees and stay price."""
        return self.price_per_night + self.entrance_kids + self.entrance_adults

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])

    class Meta:
        unique_together = ['user', 'resort'] 

    def __str__(self):
        return f"{self.user} rated {self.resort} - {self.rating}"
    
class Message(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name="messages", help_text="Resort this message is related to")
     comment = models.TextField(null=True, blank=True, help_text="User's comment or feedback")
     created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the comment was added")
     updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the resort was last updated")
    
     def __str__(self):
         return f"Message from {self.user} on {self.created_at}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, related_name='favorite_resorts', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} likes {self.resort.name}"
    
class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name="visits")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} visited {self.resort} on {self.timestamp}"

