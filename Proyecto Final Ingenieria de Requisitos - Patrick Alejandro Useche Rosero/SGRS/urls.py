"""
URL configuration for SGRS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sistema import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name ='inicio'),
    path('registrarse/', views.registrarse, name = 'registrarse'),
    path('iniciarsesion/', views.iniciar_sesion, name = 'iniciar_sesion'),
    path('cerrarsesion/', views.cerrar_sesion, name = 'cerrar_sesion'),
    path('registrarreclamo/', views.registrar_reclamo, name = 'registrar_reclamo'),
    path('registrarsolicitud/', views.registrar_solicitud, name = 'registrar_solicitud'),
    path('seguimientoestado/', views.realizar_seguimiento, name = 'seguimiento_estado'),
    path('historialreclamos/', views.visualizar_reclamos, name = 'visualizar_reclamos'),
    path('historialsolicitudes/', views.visualizar_solicitudes, name = 'visualizar_solicitudes'),
    path('cambiarestado/', views.cambiar_estado, name = 'cambiar_estado'),
    path('gestionarpermisos/', views.gestionar_permisos, name = 'gestionar_permisos'),
    path('obtener-rol-actual/', views.obtener_rol_actual, name = 'obtener_rol_actual'),
]
