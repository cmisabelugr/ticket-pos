from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(AuthLink)
admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Order)
admin.site.register(Seat)
admin.site.register(PreReservation)