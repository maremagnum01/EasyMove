from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Usuario
from .models import Usuario, Mudanza
from .models import Mudanza, Resena

class RegistroClienteForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'CLIENTE'
        if commit:
            user.save()
        return user

class RegistroEmpresaForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        
        # 1. Sacamos 'zona_cobertura' y agregamos los 4 campos específicos
        fields = [
            'username', 'email', 'cuit', 'telefono', 
            'direccion_base', 'vehiculo_principal', 
            'tiene_seguro', 'ofrece_embalaje_seguro',
            'cubre_caba', 'cubre_amba', 'cubre_resto_pba', 'cubre_interior' # <--- NUEVOS
        ]
        
        # 2. Le damos diseño Bootstrap a los checkboxes para que se vean como switches
        widgets = {
            'tiene_seguro': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'ofrece_embalaje_seguro': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'cubre_caba': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'cubre_amba': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'cubre_resto_pba': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'cubre_interior': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'EMPRESA'
        if commit:
            user.save()
        return user
    
class MudanzaForm(forms.ModelForm):
    class Meta:
        model = Mudanza
        # Agregamos los CPs a la lista de fields
        fields = ['direccion_origen', 'codigo_postal_origen', 'direccion_destino', 'codigo_postal_destino', 'tamano', 'fecha_mudanza','solicita_servicio_premium']
        widgets = {
            'direccion_origen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Corrientes 1234, CABA'}),
            'codigo_postal_origen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1046'}),
            
            'direccion_destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle 8 Nro 500, La Plata'}),
            'codigo_postal_destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1900'}),
            
            'tamano': forms.Select(attrs={'class': 'form-select'}),
            'fecha_mudanza': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'solicita_servicio_premium': forms.CheckboxInput(attrs={
                'class': 'form-check-input', 
                'role': 'switch', 
                'id': 'switchPremium'
            }),
        }
        
class ServicioPremiumForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['ofrece_embalaje_seguro', 'descripcion_servicio_premium']
        widgets = {
            'ofrece_embalaje_seguro': forms.CheckboxInput(attrs={
                'class': 'form-check-input', 
                'id': 'toggleServicio'
            }),
            'descripcion_servicio_premium': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej: Ofrecemos grabación con bodycams, inventario detallado de cajas y peones especializados...'
            }),
        }
        
class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Mudanza
        fields = ['distancia_km', 'tipo_viaje', 'costo_distancia', 'costo_operarios', 'costo_premium', 'cargos_extra', 'detalle_cargos_extra', 'precio', 'fecha_propuesta']
        widgets = {
            'distancia_km': forms.NumberInput(attrs={'class': 'form-control bg-light', 'readonly': 'readonly'}),
            'tipo_viaje': forms.TextInput(attrs={'class': 'form-control bg-light', 'readonly': 'readonly'}),
            
            # Agregamos la clase 'input-costo' para que el JavaScript los detecte y sume
            'costo_distancia': forms.NumberInput(attrs={'class': 'form-control input-costo'}),
            'costo_operarios': forms.NumberInput(attrs={'class': 'form-control input-costo'}),
            'costo_premium': forms.NumberInput(attrs={'class': 'form-control input-costo'}),
            'cargos_extra': forms.NumberInput(attrs={'class': 'form-control input-costo'}),
            'detalle_cargos_extra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Peajes, subir 3 pisos por escalera...'}),
            
            # El precio final se calculará solo, pero lo dejamos readonly para que no lo fuercen
            'precio': forms.NumberInput(attrs={'class': 'form-control fw-bold bg-success text-white', 'readonly': 'readonly', 'id': 'precioTotal'}),
            'fecha_propuesta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_fecha_propuesta(self):
        # Tu validación de fechas intacta
        fecha_propuesta = self.cleaned_data.get('fecha_propuesta')
        fecha_creacion = self.instance.fecha_creacion.date()
        if fecha_propuesta <= fecha_creacion:
            raise forms.ValidationError("La fecha de mudanza debe ser posterior al día en que el cliente realizó la solicitud.")
        return fecha_propuesta
    
    
class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.Select(attrs={'class': 'form-select form-select-lg fw-bold text-warning bg-dark'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': '¿Llegaron a tiempo? ¿Cuidaron tus muebles? Contá tu experiencia...'
            })
        }