from datetime import datetime, timedelta
from http.client import HTTPResponse
from pickle import TRUE
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.http import FileResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from pdfrw import PdfWriter, PdfReader
from io import BytesIO
from .ticket_creator import *
import json
from django.views.decorators.clickjacking import xframe_options_exempt



from .models import *
from .forms import OrderForm, PosUserForm
# Create your views here.

def home(req):
    return HttpResponse("Sistema de venta de entradas. No hay página pública")

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
        return redirect('pos_home')

    except:
        return HttpResponse("Enlace no valido")

@login_required
def pos_home(req):
    e = Event.objects.filter(active=True).order_by('datetime').all()
    user_orders = req.user.order_set.all()
    tickets_sold_user = sum(o.ticket_set.count() for o in user_orders)
    debt_user = sum(o.ticket_set.count()*o.event.ticket_price for o in req.user.order_set.filter(paid=True, free_order=False).all())
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
    num_seats = len(seats)
    error = False
        
    if req.method == "POST":
        f = OrderForm(req.POST)
        
        if f.is_valid():
            order = f.save(commit=False)
            order.event = e
            order.creator = req.user
            order.save()
            return redirect('activate_tickets',order.id)
        else:
            error = True
            context = {
                'event': e,
                'username': req.user.first_name,
                'user' : req.user,
                'seats' : seats,
                'num_seats' : num_seats,
                'form' : f,
                'error' : error
            }
            return render(req, "order_form.html", context=context)

    else:
        f = OrderForm()
        f.paid=True
        context = {
        'event': e,
        'username': req.user.first_name,
        'user' : req.user,
        'seats' : seats,
        'num_seats' : num_seats,
        'form' : f,
        'error' : error
    }

    return render(req, "order_form.html", context=context)
    
    pass


@login_required
def pos_activate_tickets(req, order_id):
    o = Order.objects.get(id=order_id)
    e = o.event

    p = PreReservation.objects.filter(event = e, user = req.user, session_id = req.session.session_key).all()
    seats = [x.seat for x in p ]
    for s in seats:
        q = s.ticket_set.filter(order__event=e)
        if q.exists():
            s.is_assigned = q.first().id
        else:
            s.is_assigned = False
    num_seats = len(seats)
    context = {
        'event': o.event,
        'order': o,
        'username': req.user.first_name,
        'user' : req.user,
        'seats' : seats,
        'num_seats' : num_seats,
        'form' : OrderForm(),
    }

    return render(req, "activate_tickets.html", context=context)
    
    pass

@login_required
def pos_api_activate(req, order_id):
    if req.method =="POST":
        error = False
        o = Order.objects.get(id=order_id)
        ticket_id = req.POST.get('ticket_code',"")
        action = req.POST.get("action", "free")
        seat_code = req.POST.get('seat_code',"")
        if action == "book":
            try:
                t = Ticket.objects.get(qr_text=ticket_id)
            except:
                error = True
                return HttpResponse(json.dumps({
                        'status' : 'error',
                        'reason' : 'notValid'
                    }))
            if t.seat:
                return HttpResponse(json.dumps({
                    'status' : 'error',
                    'reason' : 'usedTicket'
                }))
            try:
                seat_row = int(seat_code[1:3])
                seat_col = int(seat_code[4:])
                s = Seat.objects.get(row=seat_row, column=seat_col, venue = o.event.venue)
                if s.is_occupied(o.event):
                    error = True
                    return HttpResponse(json.dumps({
                    'status' : 'error',
                    'reason' : 'bookedSeat'
                }))
            except:
                error = True
                return HttpResponse(json.dumps({
                    'status' : 'error',
                    'reason' : 'badSeat'
                }))
            t.seat = s
            t.order = o
            t.paid = o.paid or o.free_order
            t.save()
            return HttpResponse(json.dumps({
                    'status' : 'ok',
                    'reason' : 'bookedCorrectly',
                    'ticket_serial' : t.id
                }))
        if action == "free":
            try:
                t = Ticket.objects.get(id=ticket_id)
                t.seat = None
                t.order = None
                t.save()
                return HttpResponse(json.dumps({
                        'status' : 'ok',
                        'reason' : 'freedTicket'
                    }))
            except:
                return HttpResponse(json.dumps({
                        'status' : 'error',
                        'reason' : 'notValid'
                    }))

    else:
        return HttpResponseBadRequest("Try again, invalid request")

@login_required
def pos_order_info(req, order_id):
    o = Order.objects.get(id=order_id)
    e = o.event
    tickets = o.ticket_set.all()
    PreReservation.objects.filter(event=e, user=req.user, session_id=req.session.session_key).delete()

    context = {
        'event': o.event,
        'order': o,
        'ticket_set' : tickets,
        'num_seats' : len(tickets),
        'username': req.user.first_name,
        'user' : req.user,
        'total_price' : len(tickets)*o.event.ticket_price
    }

    return render(req, "order_info.html", context=context)
    pass

@login_required
def pos_order_completed(req):
    pass

@login_required
def pos_cancel_list(req):
    orders = Order.objects.filter(creator=req.user).all()
    for o in orders:
        o.total_price = o.ticket_set.count()*o.event.ticket_price
    context = {
        'orders' : orders,
        'username' : req.user.first_name
    }

    return render(req, "order_list.html", context=context)

@login_required
def pos_order_cancel(req, order_id):
    try:
        o = Order.objects.get(id=order_id, creator=req.user)
        o.delete()
        return redirect('order_list')
    except:
        return HttpResponse("Bad Request")
    pass

def pos_order_download_tickets(req, order_id):
    try:
        o = Order.objects.get(id=order_id)
        tickets = o.ticket_set.all()
        result = PdfWriter()
        for t in tickets.all():
            if t.order:
                result.addPage(PdfReader(generate_ticket_complete(t.id, t.qr_text, t.order.event.datetime.day)).pages[0])
            else:
                result.addPage(PdfReader(generate_ticket(t.id, t.qr_text)).pages[0])
        file = BytesIO()
        result.write(file)
        file.seek(0)
        return FileResponse(file, as_attachment=True, filename='entradas_pedido_{}.pdf'.format(order_id))
    except:
        return HttpResponse("Bad Request")

@login_required
def pos_order_pay(req, order_id):
    try:
        o = Order.objects.get(id=order_id, creator=req.user)
        o.paid = True
        o.save()
        return redirect('order_list')
    except:
        return HttpResponse("Bad Request")

@login_required
def pos_ticket_cancel(req,qr_text):
    pass

@login_required
def door_intro(req):
    e = Event.objects.filter(active=True).order_by('datetime').all()
    return render(req, 'door_event_selection.html', context={'events':e})

@login_required
def door_func_selection(req, event_id):
    e = Event.objects.get(id=event_id)
    return render(req, 'door_function_selection.html', context={'e':e})

@login_required
def door_ticket_verify(req, event_id):
    e = Event.objects.get(id=event_id)
    return render(req, 'door_ticket_verify.html', context={'e':e})
    pass

@login_required
def door_ticket_verify_api(req, event_id):
    if req.method =="POST":
        error = False
        e = Event.objects.get(id=event_id)
        ticket_id = req.POST.get('ticket_code',"")
        action = req.POST.get("action", "verify")
        try:
            t = Ticket.objects.get(qr_text=ticket_id)
            if not t.order:
                return HttpResponse(json.dumps({'status':'blankTicket'}))
            if t.order.event != e:
                return HttpResponse(json.dumps({'status':'otherEvent'}))
            if not (t.order.paid or t.order.free_order or t.paid):
                return HttpResponse(json.dumps({'status':'notPayed'}))
            if t.checkedin:
                return HttpResponse(json.dumps({'status':'checkedIn'}))
            else:
                return HttpResponse(json.dumps({'status':'ok', 'ticket_serial' : t.id, 'seat_code' : t.seat.local_code}))
        except Ticket.DoesNotExist:
            return HttpResponse(json.dumps({'status':'invalidTicket'}))
    else:
        return HttpResponseBadRequest()
    pass

@login_required
def office_scan_ticket(req, event_id):
    e = Event.objects.get(id=event_id)
    return render(req, 'office_scan_ticket.html', context={'e':e})
    pass

@login_required
def office_pay_ticket(req, event_id, qr_text):
    e = Event.objects.get(id=event_id)
    t = Ticket.objects.get(qr_text=qr_text)
    return render(req, 'office_pay_ticket.html', context={'e':e, 't':t})
    pass

@login_required
def office_pay_ticket_db(req, event_id, qr_text):
    e = Event.objects.get(id=event_id)
    t = Ticket.objects.get(qr_text=qr_text)
    t.paid = True
    t.save()
    return redirect('office_scan',e.id)
    pass


@login_required
def door_accomodate_scan(req, event_id):
    e = Event.objects.get(id=event_id)
    return render(req, 'accomodate_scan.html', context={'e':e})
    pass 

@login_required
def door_accomodate_map(req, event_id):
    e = Event.objects.get(id=event_id)
    qr_lists = req.POST['tickets'].split(',')
    seats = []
    for qr in qr_lists:
        seats.append(Ticket.objects.get(qr_text=qr).seat)

    order_seats = seats
    event = e
    seats = event.venue.seat_set.order_by("row").all()
    num_columns = event.venue.seat_set.aggregate(Max("column"))['column__max']
    num_rows = event.venue.seat_set.aggregate(Max("row"))['row__max']

    seat_map = []

    for row in range(1,num_rows+1):
        row_seats = event.venue.seat_set.filter(row = row).all()
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
            if s in order_seats:
                s.status = "Yours"
            else:
                s.status = "Free"
            render_row.append(s)
        render_row.append("A")
        for s in row[1]:
            if s in order_seats:
                s.status = "Yours"
            else:
                s.status = "Free"
            render_row.append(s)
        for i in range(max_even-len(row[1])):
            render_row.append("E")
        seat_map_render.append(render_row)
    
    context = {
        'seats' : order_seats,
        'seat_map' : seat_map_render,
        'num_columns' : num_columns,
        'num_rows' : num_rows,
        'qr_tickets' : req.POST['tickets'],
        'e':e
    }
    return render(req, "accomodate_map.html", context=context)
    
    pass

@login_required
def door_accomodate_checkin(req, event_id):
    e = Event.objects.get(id=event_id)
    qr_lists = req.POST['tickets'].split(',')
    seats = []
    for qr in qr_lists:
        t = Ticket.objects.get(qr_text=qr)
        t.checkedin = True
        t.save()
    return redirect('accomodate_scan', e.id)
    pass

def ticket_detail(req, qr_text):
    try:
        t = Ticket.objects.get(qr_text=qr_text)
        error = False
        if t.order:
            order_seats = [x.seat for x in t.order.ticket_set.all()]
            event = t.order.event
            seats = event.venue.seat_set.order_by("row").all()
            num_columns = event.venue.seat_set.aggregate(Max("column"))['column__max']
            num_rows = event.venue.seat_set.aggregate(Max("row"))['row__max']

            seat_map = []

            for row in range(1,num_rows+1):
                row_seats = event.venue.seat_set.filter(row = row).all()
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
                    if s in order_seats:
                        s.status = "Free"
                        if s == t.seat:
                            s.status = "Yours"
                    else:
                        s.status = "Blocked"
                    render_row.append(s)
                render_row.append("A")
                for s in row[1]:
                    if s in order_seats:
                        s.status = "Free"
                        if s == t.seat:
                            s.status = "Yours"
                    else:
                        s.status = "Blocked"
                    render_row.append(s)
                for i in range(max_even-len(row[1])):
                    render_row.append("E")
                seat_map_render.append(render_row)
            
            context = {
                'error' :error,
                'seat_map' : seat_map_render,
                'ticket' : t,
                'num_columns' : num_columns,
                'num_rows' : num_rows
            }
            return render(req, "ticket_info.html", context=context)
        else:
            return render(req, "ticket_free.html")



    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
    pass

@xframe_options_exempt
def ticket_pdf_single(req, qr_text):
    try:
        t = Ticket.objects.get(qr_text=qr_text)
        print(t)
        if t.order:
            return HttpResponse(generate_ticket_complete(t.id, t.qr_text, t.order.event.datetime.day), content_type='application/pdf')
        else:
            return FileResponse(generate_ticket(t.id, t.qr_text), as_attachment=False, filename="ticket.pdf")
    except Exception as e:
        print(e)
        return HttpResponseBadRequest()
    pass

@login_required
def pos_users_list(req):
    if not req.user.is_staff:
        return HttpResponseForbidden()
    users = User.objects.exclude(username=req.user.username).all()
    for u in users:
        u.tickets_sold = sum(o.ticket_set.count() for o in u.order_set.all())
        u.debt = sum(o.ticket_set.count()*o.event.ticket_price for o in u.order_set.filter(paid=True, free_order=False).all())
        u.reserved = sum(o.ticket_set.count() for o in u.order_set.filter(paid=False, free_order=False).all())
        u.paid_tickets = u.tickets_sold-u.reserved
        u.authlink = u.authlink_set.first()
    context = {
        'users' : users,
    }

    return render(req, 'pos_users_list.html', context=context)

@login_required
def pos_users_new(req):
    if not req.user.is_staff:
        return HttpResponseForbidden()
    
    if req.method == "POST":
        f = PosUserForm(req.POST)
        if f.is_valid():
            u = User()
            u.username = f.cleaned_data['username']
            u.first_name = f.cleaned_data['first_name']
            u.save()
            a = AuthLink()
            a.user = u
            a.save()
            return redirect('staff_pos_list')
        else:
            return render(req, "pos_users_new.html", context={'error': True, 'form':f})
    else:
        return render(req, "pos_users_new.html", context={'error': False, 'form': PosUserForm()})
