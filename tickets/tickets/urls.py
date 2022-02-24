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
from pos.views import pos_order_form, whoami, authlink, pos_home, pos_seat_selection

urlpatterns = [
    path('admin/', admin.site.urls),
    path('whoami/', whoami),
    path('authpos/<str:link>/', authlink),
    path('pos/home/', pos_home, name="pos_home"),
    path('pos/seat_selection/<int:id>/', pos_seat_selection, name="seat_selection"),
    path('pos/order_form/<int:event_id>/', pos_order_form, name="order_form"),
]
