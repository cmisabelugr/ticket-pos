from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .models import *
# Create your views here.

def whoami(req):
    print(req.user)
    return HttpResponse("Eres {}".format(req.user))

def authlink(req, link):
    try:
        a = AuthLink.objects.filter(text=link).first()
        login(req, a.user)
        return HttpResponse("Logueado con éxito")

    except:
        return HttpResponse("Enlace no valido")

@login_required
def pos_home(req):
    e = Event.objects.filter(active=True).order_by('datetime').all()
    user_orders = req.user.order_set.all()
    tickets_sold_user = sum(o.ticket_set.count() for o in user_orders)
    debt_user = sum(o.ticket_set.count()*o.event.ticket_price for o in req.user.order_set.filter(paid=False).all())
    context = {
        'events': e,
        'username': req.user.first_name,
        'sold_by_user' : tickets_sold_user,
        'debt' : debt_user
    }

    return render(req, "pos_home.html", context=context)

@login_required
def pos_seat_selection(req, id):
    pass

@login_required
def pos_order_info(req):
    pass


@login_required
def pos_activate_tickets(req):
    pass

@login_required
def pos_order_info(req):
    pass

@login_required
def pos_order_completed(req):
    pass

@login_required
def pos_cancel_list(req):
    pass

@login_required
def pos_order_cancel(req, id):
    pass

@login_required
def pos_ticket_cancel(req,qr_text):
    pass

@login_required
def door_ticket_verify(req):
    pass

@login_required
def office_scan_ticket(req):
    pass

@login_required
def office_pay_ticket(req):
    pass

@login_required
def door_accomodate_home(req):
    pass

@login_required
def door_accomodate_scan(req):
    pass

@login_required
def door_accomodate_map(req):
    pass

@login_required
def door_accomodate_checkin(req):
    pass