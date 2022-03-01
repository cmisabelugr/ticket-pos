from django.contrib import admin
from django.http import FileResponse
from pdfrw import PdfWriter, PdfReader
from io import BytesIO


from .models import *
from .ticket_creator import *

class TicketAdmin(admin.ModelAdmin):
    list_display = ("__str__", 'is_assigned')
    actions = ['generate_tickets']

    def generate_tickets(self, req, q):
        result = PdfWriter()
        for t in q.all():
            if t.order:
                result.addPage(PdfReader(generate_ticket_complete(t.id, t.qr_text, t.order.event.datetime.day)).pages[0])
            else:
                result.addPage(PdfReader(generate_ticket(t.id, t.qr_text)).pages[0])
        file = BytesIO()
        result.write(file)
        file.seek(0)
        return FileResponse(file, as_attachment=True, filename='attempt1.pdf')
    generate_tickets.short_description = "Generar PDFs"



# Register your models here.
admin.site.register(AuthLink)
admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Order)
admin.site.register(Seat)
admin.site.register(PreReservation)