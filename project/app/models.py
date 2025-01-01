from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe


class User(AbstractUser):
     name = models.CharField(max_length=200, null=True)
     email = models.EmailField(unique=True, null=True)
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
     price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
     entrance_kids = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative], default=0.00)
     entrance_adults = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative], default=0.00)
     cottage = models.CharField(max_length=100, default="Default Cottage Name")  # Example field
     price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
     contact_number = models.CharField(max_length=20, help_text="Contact phone number")
     resort_image = models.ImageField(upload_to='resorts/', default='resorts/paradise.jpg', blank=True, help_text="Image of the resort")
     created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the resort was added")
     updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the resort was last updated")

     def admin_photo(self):
          return mark_safe('<img src="{}"/>'.format(self.image.url))
     admin_photo.short_description = 'image'
     admin_photo.allow_tags = True

     class Meta:
         ordering =['-updated_at', '-created_at']
    
     def __str__(self):
         return self.name


class Message(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name="messages", help_text="Resort this message is related to")
     comment = models.TextField(null=True, blank=True, help_text="User's comment or feedback")
     created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the comment was added")
     updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the resort was last updated")
    
     def __str__(self):
         return f"Message from {self.user} on {self.created_at}"


