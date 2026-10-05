from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, TemplateView
from .models import Cliente, Cuenta, Etiqueta, Transaccion
from .forms import RegistroForm, ClienteForm, CuentaForm, EtiquetaForm, TransaccionForm
from .queries import resumen_sql, cuentas_sql


class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("login")
    extra_context = {"titulo": "Crear cuenta de usuario"}

    def form_valid(self, form):
        response = super().form_valid(form)
        Cliente.objects.create(usuario=self.object, nombre=form.cleaned_data["nombre"])
        messages.success(self.request, "Registro completado. Ya puedes iniciar sesión.")
        return response


class ClienteMixin(LoginRequiredMixin):
    @property
    def cliente(self):
        cliente, _ = Cliente.objects.get_or_create(
            usuario=self.request.user,
            defaults={"nombre": self.request.user.username},
        )
        return cliente


class InicioView(ClienteMixin, TemplateView):
    template_name = "gestion/inicio.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        cuentas = Cuenta.objects.filter(cliente=self.cliente).annotate(total=Count("movimientos"))
        contexto["cuentas"] = cuentas
        contexto["saldo"] = cuentas.aggregate(total=Sum("saldo"))["total"] or Decimal("0")
        contexto["cliente"] = self.cliente
        return contexto


class PerfilView(ClienteMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("inicio")
    extra_context = {"titulo": "Editar perfil"}

    def get_object(self, queryset=None):
        return self.cliente


class PropiosMixin(ClienteMixin):
    def get_queryset(self):
        return self.model.objects.filter(cliente=self.cliente)

    def form_valid(self, form):
        form.instance.cliente = self.cliente
        return super().form_valid(form)


class CuentaCreateView(PropiosMixin, CreateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("inicio")
    extra_context = {"titulo": "Nueva cuenta digital"}


class CuentaUpdateView(PropiosMixin, UpdateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("inicio")
    extra_context = {"titulo": "Editar cuenta"}


class CuentaDeleteView(PropiosMixin, DeleteView):
    model = Cuenta
    template_name = "gestion/confirmar.html"
    success_url = reverse_lazy("inicio")

    def form_valid(self, form):
        cuenta = self.get_object()

        if cuenta.saldo != 0 or cuenta.movimientos.exists() or cuenta.entradas.exists():
            messages.error(
                self.request,
                "Solo puedes eliminar cuentas sin saldo ni movimientos."
            )
            return redirect("inicio")

        cuenta.delete()
        messages.success(self.request, "Cuenta eliminada correctamente.")
        return redirect("inicio")


class EtiquetaListView(PropiosMixin, ListView):
    model = Etiqueta
    template_name = "gestion/etiquetas.html"
    context_object_name = "etiquetas"


class EtiquetaCreateView(PropiosMixin, CreateView):
    model = Etiqueta
    form_class = EtiquetaForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("etiquetas")
    extra_context = {"titulo": "Nueva etiqueta"}


class EtiquetaUpdateView(PropiosMixin, UpdateView):
    model = Etiqueta
    form_class = EtiquetaForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("etiquetas")
    extra_context = {"titulo": "Editar etiqueta"}


class EtiquetaDeleteView(PropiosMixin, DeleteView):
    model = Etiqueta
    template_name = "gestion/confirmar.html"
    success_url = reverse_lazy("etiquetas")


class MovimientosView(PropiosMixin, ListView):
    model = Transaccion
    template_name = "gestion/movimientos.html"
    context_object_name = "movimientos"

    def get_queryset(self):
        movimientos = super().get_queryset()
        tipo = self.request.GET.get("tipo")
        texto = self.request.GET.get("q", "").strip()
        if tipo:
            movimientos = movimientos.filter(tipo=tipo)
        if texto:
            movimientos = movimientos.filter(Q(descripcion__icontains=texto) | Q(cuenta__alias__icontains=texto))
        if self.request.GET.get("solo_confirmadas") == "1":
            movimientos = movimientos.filter(confirmada=True)
        return movimientos


class TransaccionCreateView(PropiosMixin, CreateView):
    model = Transaccion
    form_class = TransaccionForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("movimientos")
    extra_context = {"titulo": "Nuevo movimiento"}

    def get_form_kwargs(self):
        datos = super().get_form_kwargs()
        datos["cliente"] = self.cliente
        return datos


class TransaccionUpdateView(PropiosMixin, UpdateView):
    model = Transaccion
    form_class = TransaccionForm
    template_name = "gestion/form.html"
    success_url = reverse_lazy("movimientos")
    extra_context = {"titulo": "Editar movimiento"}

    def get_queryset(self):
        return super().get_queryset().filter(confirmada=False)

    def get_form_kwargs(self):
        datos = super().get_form_kwargs()
        datos["cliente"] = self.cliente
        return datos


class TransaccionDeleteView(PropiosMixin, DeleteView):
    model = Transaccion
    template_name = "gestion/confirmar.html"
    success_url = reverse_lazy("movimientos")

    def get_queryset(self):
        return super().get_queryset().filter(confirmada=False)


class ConfirmarView(ClienteMixin, View):
    def post(self, request, pk):
        movimiento = get_object_or_404(Transaccion, pk=pk, cliente=self.cliente, confirmada=False)
        cuenta = movimiento.cuenta

        if movimiento.tipo == "deposito":
            cuenta.saldo += movimiento.monto
            cuenta.save()
        elif movimiento.tipo == "retiro":
            if cuenta.saldo < movimiento.monto:
                messages.error(request, "Saldo insuficiente.")
                return redirect("movimientos")
            cuenta.saldo -= movimiento.monto
            cuenta.save()
        elif movimiento.tipo == "transferencia":
            if not movimiento.destino:
                messages.error(request, "Debes seleccionar una cuenta de destino.")
                return redirect("movimientos")
            if cuenta.saldo < movimiento.monto:
                messages.error(request, "Saldo insuficiente.")
                return redirect("movimientos")
            cuenta.saldo -= movimiento.monto
            movimiento.destino.saldo += movimiento.monto
            cuenta.save()
            movimiento.destino.save()

        movimiento.confirmada = True
        movimiento.save()
        messages.success(request, "Movimiento confirmado y saldo actualizado.")
        return redirect("movimientos")


class ReporteView(ClienteMixin, TemplateView):
    template_name = "gestion/reporte.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["resumen"] = Transaccion.objects.filter(
            cliente=self.cliente, confirmada=True
        ).values("tipo").annotate(cantidad=Count("id"), total=Sum("monto")).order_by("tipo")
        contexto["sql"] = resumen_sql(self.cliente.pk)
        contexto["cuentas_sql"] = list(cuentas_sql(self.cliente.pk))
        return contexto
