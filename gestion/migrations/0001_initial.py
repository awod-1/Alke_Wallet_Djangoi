# Generated for Alke Wallet academic project
from decimal import Decimal
import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import gestion.models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100)),
                ("telefono", models.CharField(blank=True, max_length=20)),
                ("direccion", models.CharField(blank=True, max_length=200)),
                ("fecha_registro", models.DateTimeField(auto_now_add=True)),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="cliente", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Cuenta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero", models.CharField(default=gestion.models.numero_cuenta, editable=False, max_length=32, unique=True)),
                ("alias", models.CharField(max_length=80)),
                ("saldo", models.DecimalField(decimal_places=2, default=0, max_digits=14, validators=[django.core.validators.MinValueValidator(0)])),
                ("creada", models.DateTimeField(auto_now_add=True)),
                ("activa", models.BooleanField(default=True)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="cuentas", to="gestion.cliente")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Etiqueta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=40)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="etiquetas", to="gestion.cliente")),
            ],
        ),
        migrations.CreateModel(
            name="Transaccion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("deposito","Depósito"),("retiro","Retiro"),("transferencia","Transferencia")], max_length=15)),
                ("monto", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("descripcion", models.CharField(blank=True, max_length=160)),
                ("confirmada", models.BooleanField(default=False, editable=False)),
                ("creada", models.DateTimeField(auto_now_add=True)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transacciones", to="gestion.cliente")),
                ("cuenta", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimientos", to="gestion.cuenta")),
                ("destino", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="entradas", to="gestion.cuenta")),
                ("etiquetas", models.ManyToManyField(blank=True, related_name="transacciones", to="gestion.etiqueta")),
            ],
            options={"ordering": ["-creada"]},
        ),
        migrations.AddConstraint(
            model_name="cuenta",
            constraint=models.CheckConstraint(condition=models.Q(("saldo__gte", 0)), name="saldo_no_negativo"),
        ),
        migrations.AddConstraint(
            model_name="etiqueta",
            constraint=models.UniqueConstraint(fields=("cliente", "nombre"), name="etiqueta_unica_cliente"),
        ),
        migrations.AddConstraint(
            model_name="transaccion",
            constraint=models.CheckConstraint(condition=models.Q(("monto__gt", 0)), name="monto_positivo"),
        ),
    ]
