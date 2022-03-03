"""tickets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from os import name
from django.contrib import admin
from django.urls import path
from pos.views import door_accomodate_checkin, door_accomodate_map, door_accomodate_scan, door_func_selection, door_intro, door_ticket_verify, door_ticket_verify_api, office_pay_ticket, office_pay_ticket_db, office_scan_ticket, pos_activate_tickets, pos_api_activate, pos_cancel_list, pos_order_cancel, pos_order_download_tickets, pos_order_form, pos_order_info, pos_order_pay, pos_users_list, pos_users_new, ticket_detail, ticket_pdf_single, whoami, authlink, pos_home, pos_seat_selection, home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('whoami/', whoami),
    path('authpos/<str:link>/', authlink, name="pos_auth"),
    path('pos/home/', pos_home, name="pos_home"),
    path('pos/seat_selection/<int:id>/', pos_seat_selection, name="seat_selection"),
    path('pos/order_form/<int:event_id>/', pos_order_form, name="order_form"),
    path('pos/activate_tickets/<int:order_id>/', pos_activate_tickets, name="activate_tickets"),
    
    path('pos/activate_api/<int:order_id>/', pos_api_activate, name="api_activate"),
    path('pos/order_info/<int:order_id>/', pos_order_info, name="order_info"),
    path('pos/order_list/', pos_cancel_list, name="order_list"),
    path('pos/order_cancel/<int:order_id>/', pos_order_cancel, name="cancel_order"),
    path('pos/order_pay/<int:order_id>/', pos_order_pay, name="pay_order"),
    path('pos/order_download/<int:order_id>/', pos_order_download_tickets, name="download_tickets_order"),
    path('t/<str:qr_text>/', ticket_detail, name="ticket_detail"),
    path('tpdf/<str:qr_text>/', ticket_pdf_single, name="ticket_pdf_single"),

    path('staff/pos_list/', pos_users_list, name="staff_pos_list"),
    path('staff/new/', pos_users_new, name="staff_pos_new"),

    path('door/', door_intro, name="door_event_selection"),
    path('door/func/<int:event_id>/', door_func_selection, name="door_func_selection"),
    path('door/ticket_verify/<int:event_id>/', door_ticket_verify, name="door_ticket_verify"),
    path('door/ticket_api/<int:event_id>/', door_ticket_verify_api, name="door_ticket_api"),
    path('door/office_scan/<int:event_id>/', office_scan_ticket, name="office_scan"),
    path('door/office_pay/<int:event_id>/<str:qr_text>/', office_pay_ticket, name="office_pay"),
    path('door/office_pay_db/<int:event_id>/<str:qr_text>/', office_pay_ticket_db, name="office_pay_db"),
    path('door/accomodate_scan/<int:event_id>/', door_accomodate_scan, name="accomodate_scan"),
    path('door/accomodate_map/<int:event_id>/', door_accomodate_map, name="accomodate_map"),
    path('door/accomodate_check/<int:event_id>/', door_accomodate_checkin, name="accomodate_check"),
    path('', home, name="basic_home"),




]
