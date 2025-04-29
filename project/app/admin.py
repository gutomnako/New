from django.contrib import admin
from .models import LoginHistory
from .models import Resort, Message, Location, Amenity, User, Favorite, Rating, SubAdminApplication, Notification


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

@admin.register(SubAdminApplication)
class SubAdminApplicationAdmin(admin.ModelAdmin):
    list_display = ('resort_name', 'email', 'submitted_at', 'is_reviewed', 'is_approved')
    list_filter = ('is_reviewed', 'submitted_at', 'is_approved')
    readonly_fields = ('resort_name', 'email', 'verification_permit', 'submitted_at')
    ordering = ('-submitted_at',)
    list_editable = ('is_approved',)  # Make 'is_approved' editable directly from the list view

    def has_add_permission(self, request):
        return False

    
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')

admin.site.register(Notification, NotificationAdmin)
