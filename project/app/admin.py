from django.contrib import admin
from .models import LoginHistory
from .models import Resort, Message, Location, Amenity, User, Rating


admin.site.register(User)
admin.site.register(Resort)
admin.site.register(Message)
admin.site.register(Location)
admin.site.register(Amenity)
admin.site.register(Rating)
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_logins', 'total_logouts', 'last_login', 'last_logout')
    search_fields = ('user__username',)
    list_filter = ('last_login', 'last_logout')
