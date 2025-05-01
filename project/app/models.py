from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User


class SubAdminApplication(models.Model):
    resort_name = models.CharField(max_length=100)
    location = models.CharField('Location', max_length=200, blank=True, null=True, help_text="Location of the resort")
    description = models.TextField(help_text="Brief description of the resort", blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, default='0000000000')
    amenities = models.JSONField(default=list)  # Added amenities as a JSON field to store a list
    resort_image = models.ImageField(upload_to='resorts/images/', blank=True, null=True)  # Resort Image
    verification_permit = models.ImageField(upload_to='resorts/subadmin_permits/', blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # Added to track approval status
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.resort_name
    
class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To: {self.recipient.username} - {self.message[:20]}"
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
    map_url = models.URLField(blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.ManyToManyField('Location', blank=True, related_name="resorts", help_text="Location of the resort")
    description = models.TextField(help_text="Brief description of the resort", blank=True, null=True)
    mini_description = models.TextField(help_text="Mini description of the resort", blank=True, null=True)
    amenities = models.ManyToManyField('Amenity', blank=True, related_name="resorts", help_text="Amenities available at the resort")
    favorites = models.ManyToManyField(User, through='Favorite', related_name='favorite_resorts')
    
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Room price
    entrance_kids = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative], default=0.00)
    entrance_adults = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative], default=0.00)
    cottage = models.CharField(max_length=100, default="Default Cottage Name")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Cottage price
    
    contact_number = models.CharField(max_length=20, help_text="Contact phone number")
    resort_image = models.ImageField(upload_to='resorts/', default='paradise.jpg', blank=True, help_text="Image of the resort")
    hero_image = models.ImageField(upload_to='resorts/', blank=True, null=True)
    
    room_description = models.TextField(help_text="Room description", blank=True, null=True)
    beach_description = models.TextField(help_text="Beach description", blank=True, null=True)
    activity_description = models.TextField(help_text="Activity description", blank=True, null=True)
    restricted = models.BooleanField(default=False)
    location_rating = models.FloatField(default=0.0, help_text="A score representing the resort's location")
    
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the resort was added")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the resort was last updated")

    # New fields for price range categories
    room_price_range = models.CharField(max_length=10, choices=[('Low', 'Low'), ('Average', 'Average'), ('High', 'High')], default='Low')
    cottage_price_range = models.CharField(max_length=10, choices=[('Low', 'Low'), ('Average', 'Average'), ('High', 'High')], default='Low')

    class Meta:
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return self.name

   
    def get_map_url(self):
        """Return Google Map embed link based on coordinates if available."""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q={self.latitude},{self.longitude}"
        else:
            return self.map_url
        
    @property
    def total_price(self):
        """Compute the total price including entrance fees and stay price based on room and cottage ranges."""
        
        # Room price logic based on selected range
        if self.room_price_range == 'Low':
            room_price = 999  # Or another value that fits the 'Low' range
        elif self.room_price_range == 'Average':
            room_price = 2000  # Or another value that fits the 'Average' range
        elif self.room_price_range == 'High':
            room_price = 3000  # Or another value that fits the 'High' range

        # Cottage price logic based on selected range
        if self.cottage_price_range == 'Low':
            cottage_price = 999  # Adjust this to fit the 'Low' range for the cottage
        elif self.cottage_price_range == 'Average':
            cottage_price = 2000  # Adjust this to fit the 'Average' range for the cottage
        elif self.cottage_price_range == 'High':
            cottage_price = 3000  # Adjust this to fit the 'High' range for the cottage

        # Return the total price including room and cottage prices and entrance fees
        return room_price + cottage_price + self.entrance_kids + self.entrance_adults
    
    @property
    def room_rate_display(self):
        """Return the price range based on room price range."""
        if self.room_price_range == 'Low':
            return "Low: 999 or below"
        elif self.room_price_range == 'Average':
            return "Average: 1000 - 2999"
        elif self.room_price_range == 'High':
            return "High: 3000 or more"

    @property
    def cottage_rate_display(self):
        """Return the price range based on cottage price range."""
        if self.cottage_price_range == 'Low':
            return "Low: 999 or below"
        elif self.cottage_price_range == 'Average':
            return "Average: 1000 - 2999"
        elif self.cottage_price_range == 'High':
            return "High: 3000 or more"


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

class RoomImage(models.Model):
    resort = models.ForeignKey('Resort', on_delete=models.CASCADE, related_name='room_images')
    image = models.ImageField(upload_to='resorts/rooms/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resort} - Room Image"


class BeachImage(models.Model):
    resort = models.ForeignKey('Resort', on_delete=models.CASCADE, related_name='beach_images')
    image = models.ImageField(upload_to='resorts/beaches/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resort} - Beach Image"


class ActivityImage(models.Model):
    resort = models.ForeignKey('Resort', on_delete=models.CASCADE, related_name='activity_images')
    image = models.ImageField(upload_to='resorts/activities/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resort} - Activity Image"
