from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

@register.filter
def clp(valor):
    """Formatea un número como peso chileno, sin decimales: $25.000 CLP."""
    try:
        numero = Decimal(valor or 0)
    except (InvalidOperation, TypeError, ValueError):
        numero = Decimal("0")
    entero = int(numero.quantize(Decimal("1")))
    return f"${entero:,}".replace(",", ".") + " CLP"
