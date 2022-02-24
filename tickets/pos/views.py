from datetime import datetime, timedelta
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Max


from .models import *
# Create your views here.

def is_occupied_or_prereserved(seat, e):
    # TODO: Comprobar también si no hay una prereserva y sacar un 0, 1 o 2. Porque puede estar reservado por el propio usuario. Tal vez queramos convertir esto a una puñetera annotation.
    return seat.is_occupied(e)

def is_prerreserved(seat, event, req):
        p = PreReservation.objects.filter(event =event, seat = seat)
        if p.exists():
            p1 = p.first()
            expiry = (p1.datetime + timedelta(minutes=5)).timestamp()
            now = timezone.now().timestamp()
            if expiry < now:
                p1.delete()
                if seat.is_occupied(event):
                    return "Blocked"
                else:
                    return "Free"
            if p1.user == req.user:
                if p1.session_id == req.session.session_key:
                    return "Yours"
                else:
                    return "Blocked"
            else:
                return "Blocked"
        else:
            if seat.is_occupied(event):
                return "Blocked"
            else:
                return "Free"


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
    e = Event.objects.filter(id=id).first()

    seats = e.venue.seat_set.order_by("row").all()
    num_columns = e.venue.seat_set.aggregate(Max("column"))['column__max']
    num_rows = e.venue.seat_set.aggregate(Max("row"))['row__max']

    seat_map = []

    for row in range(1,num_rows+1):
        row_seats = e.venue.seat_set.filter(row = row).all()
        odd = []
        even = []
        for s in row_seats:
            if s.column %2==0:
                even.append(s)
            else: 
                odd.append(s)
        odd.sort(key=lambda x: x.column, reverse=True)
        even.sort(key=lambda x: x.column)
        seat_map.append([odd, even])

    max_odd = max([len(x[0]) for x in seat_map])
    max_even = max([len(x[1]) for x in seat_map])

    seat_map_render = []

    for row in seat_map:
        render_row = []
        for i in range(max_odd-len(row[0])):
            render_row.append("E")
        for s in row[0]:
            s.status = is_prerreserved(s, e, req)
            render_row.append(s)
        render_row.append("A")
        for s in row[1]:
            s.status = is_prerreserved(s, e, req)
            render_row.append(s)
        for i in range(max_even-len(row[1])):
            render_row.append("E")
        seat_map_render.append(render_row)

    #print(seat_map_render)
    
    print(req.session.session_key)


    context = {
        'event': e,
        'username': req.user.first_name,
        'num_columns' : num_columns,
        'num_rows' : num_rows,
        'seat_map' : seat_map_render
    }

    return render(req, "seat_map.html", context=context)
    pass

@login_required
def pos_order_form(req, event_id):
    e = Event.objects.filter(id=event_id).first()
    p = PreReservation.objects.filter(event = e, user = req.user, session_id = req.session.session_key).all()
    seats = [x.seat for x in p ]
    for s in seats:
        q = s.ticket_set.filter(order__event=e)
        if q.exists():
            s.is_assigned = q.first().id
        else:
            s.is_assigned = False
        
    

    context = {
        'event': e,
        'username': req.user.first_name,
        'seats' : seats,
    }

    return render(req, "order_form.html", context=context)
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