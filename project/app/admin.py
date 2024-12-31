from django.contrib import admin

from .models import Resort, Message, Location, Amenity, User


admin.site.register(User)
admin.site.register(Resort)
admin.site.register(Message)
admin.site.register(Location)
admin.site.register(Amenity)


