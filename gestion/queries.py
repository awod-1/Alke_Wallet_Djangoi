from django.db import connection
from .models import Cuenta

def resumen_sql(cliente_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT tipo, COUNT(*), SUM(monto) FROM gestion_transaccion "
            "WHERE cliente_id = %s AND confirmada = %s GROUP BY tipo ORDER BY tipo",
            [cliente_id, True],
        )
        return cursor.fetchall()

def cuentas_sql(cliente_id):
    return Cuenta.objects.raw(
        "SELECT * FROM gestion_cuenta WHERE cliente_id = %s ORDER BY id",
        [cliente_id],
    )
