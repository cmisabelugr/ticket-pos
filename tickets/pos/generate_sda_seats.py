from pos.models import Seat, Venue

v = Venue()
v.name = "CM Isabel la Católica - Salón de actos"
v.has_seats = True
v.num_seats = 145
v.save()

for row in range(1,12):
    for column in range(1,15):
        if (row==7): 
            if (column%2==0):
                s = Seat(venue=v, row=row, column=column)
                s.save()
        else:
            if column!=13:
                s = Seat(venue=v, row=row, column=column)
                s.save()
        
for column in range(1,9):
    s = Seat(venue=v, row=12, column=column)
    s.save()

print("CMISDA listo")