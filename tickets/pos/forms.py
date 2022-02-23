from django import forms
from .models import Order

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ("customer_name", "customer_email", "customer_phone", "paid", "free_order")