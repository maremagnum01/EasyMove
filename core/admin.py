from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Mudanza, Resena

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos de EasyMove', {
            'fields': (
                'rol', 'reputacion', 'cuit', 'telefono', 'direccion_base', 
                'vehiculo_principal', 'zona_cobertura', 'tiene_seguro', 'ofrece_embalaje_seguro'
            )
        }),
    )
    list_display = ('username', 'rol', 'reputacion', 'cuit', 'vehiculo_principal')
    
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Mudanza)
admin.site.register(Resena) # Registramos las reseñas