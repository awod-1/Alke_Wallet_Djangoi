from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from gestion.views import RegistroView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("registro/", RegistroView.as_view(), name="registro"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("gestion.urls")),
]
