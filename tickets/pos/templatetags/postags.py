from django import template

register = template.Library()

@register.filter(name="seatoccupied")
def is_occupied(seat, e):
    # TODO: Comprobar también si no hay una prereserva y sacar un 0, 1 o 2. Porque puede estar reservado por el propio usuario. Tal vez queramos convertir esto a una puñetera annotation.
    return seat.is_occupied(e)
