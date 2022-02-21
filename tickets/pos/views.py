from curses.ascii import HT
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth import login

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
