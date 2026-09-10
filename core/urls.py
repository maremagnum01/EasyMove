from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/cliente/', views.registro_cliente, name='registro_cliente'),
    path('registro/empresa/', views.registro_empresa, name='registro_empresa'),
    path('empresas/', views.buscador_empresas, name='buscador_empresas'),
    path('empresa/<int:empresa_id>/', views.perfil_empresa, name='perfil_empresa'),
    path('solicitar/<int:empresa_id>/', views.solicitar_mudanza, name='solicitar_mudanza'),
    path('panel/empresa/', views.panel_empresa, name='panel_empresa'),
    path('panel/empresa/aceptar/<int:mudanza_id>/', views.aceptar_mudanza, name='aceptar_mudanza'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('panel/cliente/', views.panel_cliente, name='panel_cliente'),
    path('panel/cliente/cancelar/<int:mudanza_id>/', views.cancelar_mudanza, name='cancelar_mudanza'),
    path('panel/empresa/cotizar/<int:mudanza_id>/', views.cotizar_mudanza, name='cotizar_mudanza'),
    path('panel/cliente/aceptar-cotizacion/<int:mudanza_id>/', views.aceptar_cotizacion, name='aceptar_cotizacion'),
    path('panel/empresa/finalizar/<int:mudanza_id>/', views.finalizar_mudanza, name='finalizar_mudanza'),
    path('panel/cliente/resena/<int:mudanza_id>/', views.dejar_resena, name='dejar_resena'),
]