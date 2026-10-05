from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Cuenta, Etiqueta, Transaccion


def aplicar_bootstrap(formulario):
    """Aplica clases de Bootstrap a los campos del formulario."""
    for campo in formulario.fields.values():
        if isinstance(campo.widget, forms.CheckboxInput):
            campo.widget.attrs["class"] = "form-check-input"
        elif isinstance(campo.widget, (forms.Select, forms.SelectMultiple)):
            campo.widget.attrs["class"] = "form-select"
        else:
            campo.widget.attrs["class"] = "form-control"


class RegistroForm(UserCreationForm):
    nombre = forms.CharField(max_length=100, label="Nombre completo")
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "nombre", "email", "password1", "password2")
        labels = {"username": "Nombre de usuario"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ("nombre", "telefono", "direccion")
        labels = {"nombre": "Nombre", "telefono": "Teléfono", "direccion": "Dirección"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)


class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ("alias", "activa")
        labels = {"alias": "Nombre o alias de la cuenta", "activa": "Cuenta activa"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)


class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ("nombre",)
        labels = {"nombre": "Nombre de la etiqueta"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)


class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ("cuenta", "tipo", "monto", "destino", "descripcion", "etiquetas")
        labels = {
            "cuenta": "Cuenta de origen",
            "tipo": "Tipo de movimiento",
            "monto": "Monto (CLP)",
            "destino": "Cuenta de destino",
            "descripcion": "Descripción",
            "etiquetas": "Etiquetas",
        }
        help_texts = {
            "destino": "Selecciona una cuenta de destino solo para transferencias.",
            "etiquetas": "Puedes seleccionar una o más etiquetas.",
        }
        widgets = {"monto": forms.NumberInput(attrs={"step": "1", "min": "1", "placeholder": "Ej.: 25000"})}

    def __init__(self, *args, cliente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente = cliente
        self.fields["tipo"].choices = [("", "Selecciona un tipo de movimiento")] + list(Transaccion.TIPOS)
        self.fields["cuenta"].empty_label = "Selecciona una cuenta"
        self.fields["destino"].empty_label = "Sin cuenta de destino"
        if cliente:
            self.fields["cuenta"].queryset = Cuenta.objects.filter(cliente=cliente, activa=True)
            self.fields["destino"].queryset = Cuenta.objects.filter(cliente=cliente, activa=True)
            self.fields["etiquetas"].queryset = Etiqueta.objects.filter(cliente=cliente)
        aplicar_bootstrap(self)

    def clean(self):
        data = super().clean()
        cuenta, destino, tipo = data.get("cuenta"), data.get("destino"), data.get("tipo")
        if self.cliente and cuenta and cuenta.cliente_id != self.cliente.id:
            self.add_error("cuenta", "La cuenta seleccionada no es válida.")
        if tipo == "transferencia":
            if not destino or destino == cuenta:
                self.add_error("destino", "Selecciona una cuenta de destino diferente.")
        elif destino:
            self.add_error("destino", "La cuenta de destino solo se utiliza en transferencias.")
        return data
