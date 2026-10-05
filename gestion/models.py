import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

def numero_cuenta():
    return uuid.uuid4().hex.upper()

class Cliente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cliente")
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nombre

class Cuenta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="cuentas")
    numero = models.CharField(max_length=32, unique=True, default=numero_cuenta, editable=False)
    alias = models.CharField(max_length=80)
    saldo = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    creada = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    class Meta:
        ordering = ["id"]
        constraints = [models.CheckConstraint(condition=models.Q(saldo__gte=0), name="saldo_no_negativo")]
    def __str__(self):
        return f"{self.alias} · {self.numero[:8]}"

class Etiqueta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="etiquetas")
    nombre = models.CharField(max_length=40)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["cliente", "nombre"], name="etiqueta_unica_cliente")]
    def __str__(self):
        return self.nombre

class Transaccion(models.Model):
    TIPOS = [("deposito","Depósito"), ("retiro","Retiro"), ("transferencia","Transferencia")]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="transacciones")
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name="movimientos")
    destino = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name="entradas", null=True, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPOS)
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    descripcion = models.CharField(max_length=160, blank=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name="transacciones")
    confirmada = models.BooleanField(default=False, editable=False)
    creada = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-creada"]
        constraints = [models.CheckConstraint(condition=models.Q(monto__gt=0), name="monto_positivo")]
    def clean(self):
        super().clean()
        if self.cuenta_id and self.cliente_id and self.cuenta.cliente_id != self.cliente_id:
            raise ValidationError("La cuenta debe pertenecer al cliente.")
        if self.tipo == "transferencia":
            if not self.destino_id or self.destino_id == self.cuenta_id:
                raise ValidationError("Selecciona una cuenta destino distinta.")
            if self.cliente_id and self.destino.cliente_id != self.cliente_id:
                raise ValidationError("El destino debe ser una cuenta propia.")
        elif self.destino_id:
            raise ValidationError("Solo una transferencia puede tener destino.")
    def __str__(self):
        return f"{self.get_tipo_display()} · ${self.monto:,.0f} CLP".replace(",", ".")
