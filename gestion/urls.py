from django.urls import path
from . import views

urlpatterns = [
    path("", views.InicioView.as_view(), name="inicio"),
    path("perfil/", views.PerfilView.as_view(), name="perfil"),
    path("cuentas/nueva/", views.CuentaCreateView.as_view(), name="cuenta_nueva"),
    path("cuentas/<int:pk>/editar/", views.CuentaUpdateView.as_view(), name="cuenta_editar"),
    path("cuentas/<int:pk>/eliminar/", views.CuentaDeleteView.as_view(), name="cuenta_eliminar"),
    path("etiquetas/", views.EtiquetaListView.as_view(), name="etiquetas"),
    path("etiquetas/nueva/", views.EtiquetaCreateView.as_view(), name="etiqueta_nueva"),
    path("etiquetas/<int:pk>/editar/", views.EtiquetaUpdateView.as_view(), name="etiqueta_editar"),
    path("etiquetas/<int:pk>/eliminar/", views.EtiquetaDeleteView.as_view(), name="etiqueta_eliminar"),
    path("movimientos/", views.MovimientosView.as_view(), name="movimientos"),
    path("movimientos/nuevo/", views.TransaccionCreateView.as_view(), name="movimiento_nuevo"),
    path("movimientos/<int:pk>/editar/", views.TransaccionUpdateView.as_view(), name="movimiento_editar"),
    path("movimientos/<int:pk>/eliminar/", views.TransaccionDeleteView.as_view(), name="movimiento_eliminar"),
    path("movimientos/<int:pk>/confirmar/", views.ConfirmarView.as_view(), name="movimiento_confirmar"),
    path("reportes/", views.ReporteView.as_view(), name="reporte"),
]
