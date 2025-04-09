from django.contrib import admin
from .models import LoginHistory
from .models import Resort, Message, Location, Amenity, User, Favorite, Rating


admin.site.register(User)

admin.site.register(Message)
admin.site.register(Location)
admin.site.register(Amenity)
admin.site.register(Rating)
admin.site.register(Favorite)
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_logins', 'total_logouts', 'last_login', 'last_logout')
    search_fields = ('user__username',)
    list_filter = ('last_login', 'last_logout')  
@admin.register(Resort)
class ResortAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'map_url')
    search_fields = ('name',)
    list_filter = ('latitude', 'longitude')  # Optionally, filter by latitude/longitude in the admin

    # Optionally, add ordering or custom field display
    ordering = ('name',)