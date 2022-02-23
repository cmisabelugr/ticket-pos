import code
from pyexpat import model
import random, string
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils import timezone

def get_random_string():
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(6))
    return result_str
# Create your models here.
class Venue(models.Model):

    name = models.TextField(blank=False, verbose_name=_("Venue name"))
    has_seats = models.BooleanField(default=True, blank=False, verbose_name=_("Has seats"))
    num_seats = models.IntegerField(verbose_name=_("Number of seats"), blank=False, default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Venue'
        verbose_name_plural = 'Venues'
        
class Event(models.Model):
    name = models.TextField(blank=False, verbose_name="Event name")
    datetime = models.DateTimeField(blank=False, default=timezone.now)
    venue = models.ForeignKey(to=Venue, blank=False, on_delete=models.CASCADE)
    ticket_price = models.FloatField(verbose_name=_("Ticket price"), blank=False, default=0.0)
    active = models.BooleanField(verbose_name=_("Enabled"), blank=False, default=True)

    @property
    def sold_tickets(self):
        orders = self.order_set.all()
        result = 0
        for o in orders:
            result += o.ticket_set.count()
        return result

    @property
    def left_tickets(self):
        return self.venue.num_seats - self.sold_tickets
    
    def __str__(self):
        return "{} - {}".format(self.name, self.datetime)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
class Order(models.Model):

    order_time = models.DateTimeField(verbose_name=_("Order Time"),auto_now_add=True)
    customer_name = models.TextField(blank= False, verbose_name=_("Customer name"))
    customer_email = models.EmailField(blank=False, verbose_name=_("Customer email"))
    customer_phone = models.TextField(blank=True, verbose_name=_("Customer telephone (optional)"))
    paid = models.BooleanField(blank=False, default=False, verbose_name=_("Paid"))
    free_order = models.BooleanField(blank=False, default=False, verbose_name=_("Free order"))

    creator = models.ForeignKey(to=User, blank=False, verbose_name=_("Created by"), on_delete=models.CASCADE)
    event = models.ForeignKey(to=Event, blank=False, verbose_name=_("Event"), on_delete=models.CASCADE)

    @property
    def num_tickets(self):
        return self.ticket_set.count()

    def __str__(self):
        return "Order {} for {} for {}".format(self.id, self.event, self.customer_name)

    class Meta:

        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

class Seat(models.Model):

    venue = models.ForeignKey(to=Venue, verbose_name=_("Venue"), blank= False, on_delete=models.CASCADE)
    row = models.SmallIntegerField(verbose_name=_("Row"), blank=False)
    column = models.SmallIntegerField(verbose_name=_("Column"), blank=False)

    def __str__(self):
        return "Seat R{0:02d}C{1:02d} of {2}".format(self.row, self.column, self.venue)

    @property
    def local_code(self):
        return "R{0:02d}C{1:02d}".format(self.row, self.column)

    def is_occupied(self, e):
        return self.ticket_set.filter(order__event=e).exists()

    class Meta:
        unique_together = ['venue', 'row', 'column']
        verbose_name = _('Seat')
        verbose_name_plural = _('Seats')
class Ticket(models.Model):

    qr_text = models.TextField(verbose_name=_("QR Text label"), blank=False, default=get_random_string, unique=True)
    seat = models.ForeignKey(to=Seat, blank=True, default=None, on_delete=models.CASCADE)
    order = models.ForeignKey(to=Order, blank=True, default=None, on_delete=models.CASCADE)
    checkedin = models.BooleanField(default=False, blank=False)
    paid = models.BooleanField(blank=False, default=False, verbose_name=_("Paid"))


    def __str__(self):
        if self.order:
            return "Ticket {} for {}".format(self.id, self.order)
        else:
            return "Ticket {}".format(self.id)

    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')




class AuthLink(models.Model):

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name=_("AuthLink Code"), blank=False, default=get_random_string, unique=True)

class PreReservation(models.Model):
    seat = models.ForeignKey(to=Seat, blank=False, verbose_name=_("Prereserved seat"), on_delete=models.CASCADE)
    event = models.ForeignKey(to=Event, blank=False, verbose_name=_("Prereserved event"), on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, blank=False, verbose_name=_("Prereserved POS"), on_delete=models.CASCADE)
    datetime = models.DateTimeField(verbose_name=_("Prereservation time"), auto_now_add=True)
    session_id = models.TextField(verbose_name=_("POS Session"), blank=True)
