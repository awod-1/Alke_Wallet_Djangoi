from django.contrib import admin
from .models import Cliente, Cuenta, Etiqueta, Transaccion

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "usuario", "telefono", "fecha_registro")
    search_fields = ("nombre", "usuario__username")

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("alias", "numero", "cliente", "saldo", "activa")
    search_fields = ("alias", "numero", "cliente__nombre")
    readonly_fields = ("numero", "saldo", "creada")

@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cliente")

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "cliente", "cuenta", "monto", "confirmada", "creada")
    list_filter = ("tipo", "confirmada")
    readonly_fields = ("cliente", "cuenta", "destino", "tipo", "monto", "descripcion", "confirmada", "creada")
