from django import forms
from .models import Order

class OrderForm(forms.ModelForm):

    #send_by_email = forms.BooleanField(initial=True)
    class Meta:
        model = Order
        fields = ("customer_name", "customer_email", "customer_phone", "paid", "free_order")

class PosUserForm(forms.Form):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
