from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Usuario(AbstractUser):
    TIPOS_DE_ROL = (
        ('CLIENTE', 'Me quiero mudar'),
        ('EMPRESA', 'Realizo mudanzas'),
    )
    rol = models.CharField(max_length=10, choices=TIPOS_DE_ROL, default='CLIENTE')
    reputacion = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    # --- DATOS DEL PERFIL DE EMPRESA ---
    ZONAS_COBERTURA = (
        ('SOLO_CABA', 'Solo Capital Federal'),
        ('SOLO_PBA', 'Solo Provincia de Buenos Aires'),
        ('CABA_A_PBA', 'Capital Federal a Provincia'),
        ('PBA_A_CABA', 'Provincia a Capital Federal'),
        ('TODAS', 'CABA y Provincia (Ambos sentidos)'),
    )
    zona_cobertura = models.CharField(max_length=20, choices=ZONAS_COBERTURA, default='TODAS')
    ofrece_embalaje_seguro = models.BooleanField(default=False, help_text="Incluye operarios con bodycam y registro de cajas")
    descripcion_servicio_premium = models.TextField(
    blank=True, 
    null=True, 
    help_text="Describe qué incluye tu servicio extra"
)
    
    # --- NUEVOS CAMPOS REALISTAS ---
    cuit = models.CharField(max_length=11, blank=True, null=True, help_text="Solo números, sin guiones")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion_base = models.CharField(max_length=255, blank=True, null=True)
    
    TIPO_FLOTA = (
        ('FURGON', 'Furgón (Ej: Kangoo, Partner)'),
        ('CAMIONETA', 'Camioneta (Ej: F-100, Hilux)'),
        ('CAMION_CHICO', 'Camión Liviano (Ej: 350)'),
        ('CAMION_MUDANZA', 'Camión de Mudanza Grande'),
    )
    vehiculo_principal = models.CharField(max_length=20, choices=TIPO_FLOTA, blank=True, null=True)
    tiene_seguro = models.BooleanField(default=False, help_text="¿Cuenta con seguro de carga?")
    cubre_caba = models.BooleanField(default=True, verbose_name="Solo CABA")
    cubre_amba = models.BooleanField(default=True, verbose_name="AMBA (Conurbano)")
    cubre_resto_pba = models.BooleanField(default=False, verbose_name="Resto de PBA (Ej: La Plata, Costa)")
    cubre_interior = models.BooleanField(default=False, verbose_name="Interior del País")
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
    
    
class Mudanza(models.Model):
    # Estados por los que pasará el servicio
    ESTADOS = (
        ('PENDIENTE', 'Buscando transporte'),
        ('ASIGNADA', 'Transporte asignado'),
        ('COTIZADA', 'Cotizada'),
        ('FINALIZADA', 'Completada'),
    )
    
    TAMANOS = (
        ('CHICA', 'Chica (pocas cajas)'),
        ('MEDIANA', 'Mediana (muebles básicos)'),
        ('GRANDE', 'Grande (casa completa)'),
    )

    # Relacionamos al Cliente que la pide
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mudanzas_pedidas'
    )
    
    # Relacion Empresa/Fletero 
    empresa = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='mudanzas_asignadas'
    )
    
    # Datos del viaje
    direccion_origen = models.CharField(max_length=255)
    codigo_postal_origen = models.CharField(max_length=10, null=True, blank=False)
    direccion_destino = models.CharField(max_length=255)
    codigo_postal_destino = models.CharField(max_length=10, null=True, blank=False)
    solicita_servicio_premium = models.BooleanField(default=False)
    tamano = models.CharField(max_length=15, choices=TAMANOS, default='CHICA')
    fecha_mudanza = models.DateField(null=True, blank=False)
    tiene_resena = models.BooleanField(default=False)
    
    distancia_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_viaje = models.CharField(max_length=100, null=True, blank=True) # Ej: "CABA a Provincia"
    costo_distancia = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    costo_operarios = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    costo_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cargos_extra = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)
    detalle_cargos_extra = models.CharField(max_length=255, null=True, blank=True)
    
    precio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha_propuesta = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De {self.direccion_origen} a {self.direccion_destino} ({self.get_estado_display()})"


# --- NUEVO MODELO DE RESEÑAS ---
class Resena(models.Model):
    # Relación 1 a 1: Una mudanza tiene una sola reseña
    mudanza = models.OneToOneField(Mudanza, on_delete=models.CASCADE, related_name='resena')
    empresa = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resenas_recibidas')
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resenas_dadas')
    
    calificacion = models.IntegerField(choices=[
        (5, '⭐⭐⭐⭐⭐ - Excelente'),
        (4, '⭐⭐⭐⭐ - Muy Bueno'),
        (3, '⭐⭐⭐ - Bueno'),
        (2, '⭐⭐ - Regular'),
        (1, '⭐ - Malo')
    ])
    comentario = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.cliente.username} a {self.empresa.username} - {self.calificacion} Estrellas"