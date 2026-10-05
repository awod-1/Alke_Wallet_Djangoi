from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Cliente, Cuenta, Etiqueta, Transaccion
from .queries import resumen_sql, cuentas_sql


class AlkeWalletTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="paula", password="Clave12345")
        self.cliente = Cliente.objects.create(usuario=self.usuario, nombre="Paula")
        self.cuenta = Cuenta.objects.create(cliente=self.cliente, alias="Cuenta principal")
        self.ahorro = Cuenta.objects.create(cliente=self.cliente, alias="Ahorro")
        self.client.login(username="paula", password="Clave12345")

    def test_relacion_usuario_cliente(self):
        self.assertEqual(self.usuario.cliente, self.cliente)

    def test_relacion_cliente_cuentas(self):
        self.assertEqual(self.cliente.cuentas.count(), 2)

    def test_relacion_muchos_a_muchos(self):
        etiqueta = Etiqueta.objects.create(cliente=self.cliente, nombre="Compras")
        movimiento = Transaccion.objects.create(cliente=self.cliente, cuenta=self.cuenta, tipo="deposito", monto=1000)
        movimiento.etiquetas.add(etiqueta)
        self.assertEqual(movimiento.etiquetas.count(), 1)

    def test_crear_cuenta(self):
        respuesta = self.client.post(reverse("cuenta_nueva"), {"alias": "Viajes", "activa": True})
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Cuenta.objects.filter(alias="Viajes").exists())

    def test_editar_cuenta(self):
        self.client.post(reverse("cuenta_editar", args=[self.cuenta.pk]), {"alias": "Principal editada", "activa": True})
        self.cuenta.refresh_from_db()
        self.assertEqual(self.cuenta.alias, "Principal editada")

    def test_eliminar_cuenta_sin_movimientos(self):
        cuenta = Cuenta.objects.create(cliente=self.cliente, alias="Temporal")
        self.client.post(reverse("cuenta_eliminar", args=[cuenta.pk]))
        self.assertFalse(Cuenta.objects.filter(pk=cuenta.pk).exists())

    def test_confirmar_deposito(self):
        movimiento = Transaccion.objects.create(cliente=self.cliente, cuenta=self.cuenta, tipo="deposito", monto=Decimal("50000"))
        self.client.post(reverse("movimiento_confirmar", args=[movimiento.pk]))
        self.cuenta.refresh_from_db()
        self.assertEqual(self.cuenta.saldo, Decimal("50000"))

    def test_confirmar_retiro(self):
        self.cuenta.saldo = Decimal("50000")
        self.cuenta.save()
        movimiento = Transaccion.objects.create(cliente=self.cliente, cuenta=self.cuenta, tipo="retiro", monto=Decimal("10000"))
        self.client.post(reverse("movimiento_confirmar", args=[movimiento.pk]))
        self.cuenta.refresh_from_db()
        self.assertEqual(self.cuenta.saldo, Decimal("40000"))

    def test_transferencia(self):
        self.cuenta.saldo = Decimal("50000")
        self.cuenta.save()
        movimiento = Transaccion.objects.create(cliente=self.cliente, cuenta=self.cuenta, destino=self.ahorro, tipo="transferencia", monto=Decimal("20000"))
        self.client.post(reverse("movimiento_confirmar", args=[movimiento.pk]))
        self.cuenta.refresh_from_db()
        self.ahorro.refresh_from_db()
        self.assertEqual(self.cuenta.saldo, Decimal("30000"))
        self.assertEqual(self.ahorro.saldo, Decimal("20000"))

    def test_filtro_movimientos(self):
        Transaccion.objects.create(cliente=self.cliente, cuenta=self.cuenta, tipo="deposito", monto=1000, descripcion="Sueldo")
        respuesta = self.client.get(reverse("movimientos"), {"q": "Sueldo"})
        self.assertContains(respuesta, "Sueldo")

    def test_consulta_raw(self):
        cuentas = list(cuentas_sql(self.cliente.pk))
        self.assertEqual(len(cuentas), 2)

    def test_consulta_sql_personalizada(self):
        Transaccion.objects.create(cliente=self.cliente, cuenta=self.cuenta, tipo="deposito", monto=1000, confirmada=True)
        resultado = resumen_sql(self.cliente.pk)
        self.assertEqual(len(resultado), 1)
