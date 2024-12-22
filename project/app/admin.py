from django.contrib import admin

from .models import Resort, Message, Location, Amenity

admin.site.register(Resort)
admin.site.register(Message)
admin.site.register(Location)
admin.site.register(Amenity)
