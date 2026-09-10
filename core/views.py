from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroClienteForm, RegistroEmpresaForm
from .models import Usuario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegistroClienteForm, RegistroEmpresaForm, MudanzaForm
from .models import Mudanza, Usuario
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import RegistroClienteForm, RegistroEmpresaForm, MudanzaForm, ServicioPremiumForm, CotizacionForm
import requests
from .models import Mudanza, Usuario, Resena
from .forms import ResenaForm
from django.db.models import Avg

def home(request):
    return render(request, 'core/home.html')

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Inicia sesión automáticamente tras el registro
            return redirect('buscador_empresas')
    else:
        form = RegistroClienteForm()
    return render(request, 'core/registro.html', {'form': form, 'tipo': 'Cliente'})

def registro_empresa(request):
    if request.method == 'POST':
        form = RegistroEmpresaForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('panel_empresa')
    else:
        form = RegistroEmpresaForm()
    return render(request, 'core/registro.html', {'form': form, 'tipo': 'Empresa/Fletero'})

def buscador_empresas(request):
    empresas = Usuario.objects.filter(rol='EMPRESA')
    
    # Capturamos los filtros del HTML
    query_nombre = request.GET.get('q')
    filtro_premium = request.GET.get('premium')
    filtro_estrellas = request.GET.get('estrellas')
    filtro_alcance = request.GET.get('alcance') # <--- NUEVO
    
    # Aplicamos filtros
    if query_nombre:
        empresas = empresas.filter(username__icontains=query_nombre)
        
    if filtro_premium == 'on':
        empresas = empresas.filter(ofrece_embalaje_seguro=True)
        
    if filtro_estrellas:
        empresas = empresas.filter(reputacion__gte=float(filtro_estrellas))
        
    # NUEVA LÓGICA DE ALCANCE
    filtro_alcance = request.GET.get('alcance')
    
    if filtro_alcance:
        if filtro_alcance == 'caba':
            empresas = empresas.filter(cubre_caba=True)
        elif filtro_alcance == 'amba':
            empresas = empresas.filter(cubre_amba=True)
        elif filtro_alcance == 'resto_pba':
            empresas = empresas.filter(cubre_resto_pba=True)
        elif filtro_alcance == 'interior':
            empresas = empresas.filter(cubre_interior=True)
            
    empresas = empresas.order_by('-reputacion')
    
    return render(request, 'core/buscador_empresas.html', {'empresas': empresas})

def perfil_empresa(request, empresa_id):
    # Buscamos la empresa
    empresa = get_object_or_404(Usuario, id=empresa_id, rol='EMPRESA')
    
    # 1. Traemos todas las reseñas de esta empresa, de la más nueva a la más vieja
    resenas = empresa.resenas_recibidas.all().order_by('-fecha_creacion')
    
    # 2. Calculamos el promedio matemático
    promedio = resenas.aggregate(Avg('calificacion'))['calificacion__avg']
    
    # 3. Si no tiene reseñas da None, así que lo pasamos a 0. Si tiene, lo redondeamos a 1 decimal (ej: 4.5)
    if promedio is not None:
        promedio = round(promedio, 1)
    else:
        promedio = 0
        
    return render(request, 'core/perfil_empresa.html', {
        'empresa': empresa,
        'resenas': resenas,      # Pasamos la lista de comentarios al HTML
        'promedio': promedio,    # Pasamos el número promedio al HTML
    })
    
@login_required
def solicitar_mudanza(request, empresa_id):
    empresa = get_object_or_404(Usuario, id=empresa_id, rol='EMPRESA')
    
    if request.method == 'POST':
        form = MudanzaForm(request.POST)
        if form.is_valid():
            mudanza = form.save(commit=False)
            mudanza.cliente = request.user
            mudanza.empresa = empresa
            mudanza.save()
            return redirect('panel_cliente')
    else:
        form = MudanzaForm()
        
    return render(request, 'core/solicitar_mudanza.html', {
        'form': form, 
        'empresa': empresa # <-- Nos aseguramos de enviar la empresa
    })
    
@login_required
def panel_empresa(request):
    if request.user.rol != 'EMPRESA':
        return redirect('buscador_empresas')
    
    # Procesamos el botón de guardar el servicio premium
    if request.method == 'POST':
        form_servicio = ServicioPremiumForm(request.POST, instance=request.user)
        if form_servicio.is_valid():
            form_servicio.save()
            return redirect('panel_empresa')
    else:
        form_servicio = ServicioPremiumForm(instance=request.user)
    
    pendientes = Mudanza.objects.filter(empresa=request.user, estado='PENDIENTE').order_by('-fecha_creacion')
    asignadas = Mudanza.objects.filter(empresa=request.user, estado='ASIGNADA').order_by('-fecha_creacion')
    finalizadas = Mudanza.objects.filter(empresa=request.user, estado='FINALIZADA').order_by('-fecha_mudanza')
    
    return render(request, 'core/panel_empresa.html', {
        'form_servicio': form_servicio,
        'pendientes': pendientes,
        'asignadas': asignadas,
        'finalizadas': finalizadas
    })
    
@login_required
def aceptar_mudanza(request, mudanza_id):
    # Buscamos la mudanza asegurándonos que pertenezca a la empresa logueada
    mudanza = get_object_or_404(Mudanza, id=mudanza_id, empresa=request.user)
    
    if mudanza.estado == 'PENDIENTE':
        mudanza.estado = 'ASIGNADA'
        mudanza.save()
        
    return redirect('panel_empresa')

def iniciar_sesion(request):
    # 1. AUTO-DETECCIÓN: Si ya está logueado de antes, lo redirigimos directo
    if request.user.is_authenticated:
        if request.user.rol == 'EMPRESA':
            return redirect('panel_empresa')
        else:
            return redirect('buscador_empresas')

    # 2. PROCESO DE LOGIN: Si recién está poniendo sus datos
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Al validar la contraseña, detectamos el rol y lo mandamos a su lugar
            if user.rol == 'EMPRESA':
                return redirect('panel_empresa')
            else:
                return redirect('buscador_empresas')
    else:
        form = AuthenticationForm()
        
    return render(request, 'core/login.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('home')


@login_required
def panel_cliente(request):
    # Si entra una empresa por error, la mandamos a su panel
    if request.user.rol != 'CLIENTE':
        return redirect('panel_empresa')
    
    pendientes = Mudanza.objects.filter(
        cliente=request.user, 
        estado__in=['PENDIENTE', 'COTIZADA']
    ).order_by('-fecha_creacion')
    
    asignadas = Mudanza.objects.filter(
        cliente=request.user, 
        estado='ASIGNADA'
    ).order_by('-fecha_creacion')
    
    finalizadas = Mudanza.objects.filter(cliente=request.user, estado='FINALIZADA').order_by('-fecha_mudanza')
    
    return render(request, 'core/panel_cliente.html', {
        'pendientes': pendientes,
        'asignadas': asignadas,
        'finalizadas': finalizadas # <--- NUEVO
    })

@login_required
def cancelar_mudanza(request, mudanza_id):
    # Permitimos cancelar si está pendiente o si ya le pasaron presupuesto pero no lo quiere
    mudanza = get_object_or_404(Mudanza, id=mudanza_id, cliente=request.user, estado__in=['PENDIENTE', 'COTIZADA'])
    mudanza.delete()
    return redirect('panel_cliente')


def determinar_zona(direccion, cp):
    """Lógica de negocio para identificar la región"""
    texto = f"{direccion} {cp}".lower()
    if 'caba' in texto or 'capital federal' in texto or (cp and cp.startswith('1') and len(cp) == 4):
        return 'CABA'
    elif 'santa fe' in texto or 'cordoba' in texto or 'rosario' in texto or 'interior' in texto:
        return 'INTERIOR'
    else:
        return 'PROVINCIA' # Asumimos PBA por defecto si no es CABA ni Interior

def obtener_distancia_km(origen, destino):
    """Consulta a la API de Google Distance Matrix"""
    api_key = "AIzaSyD064X0eNh9iXASvTUZEjHgPtXTIchXw_k" # Pone tu clave real aquí
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origen}&destinations={destino}&key={api_key}"
    try:
        response = requests.get(url).json()
        if response['status'] == 'OK' and response['rows'][0]['elements'][0]['status'] == 'OK':
            metros = response['rows'][0]['elements'][0]['distance']['value']
            return metros / 1000.0
    except Exception:
        pass
    return 15.0 # Kilometraje por defecto si la API falla o la dirección es ambigua


@login_required
def cotizar_mudanza(request, mudanza_id):
    mudanza = get_object_or_404(Mudanza, id=mudanza_id, empresa=request.user, estado='PENDIENTE')
    
    if request.method == 'POST':
        form = CotizacionForm(request.POST, instance=mudanza)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.estado = 'COTIZADA'
            cotizacion.save()
            return redirect('panel_empresa')
    else:
        # 1. Obtenemos datos
        distancia = obtener_distancia_km(mudanza.direccion_origen, mudanza.direccion_destino)
        zona_origen = determinar_zona(mudanza.direccion_origen, mudanza.codigo_postal_origen)
        zona_destino = determinar_zona(mudanza.direccion_destino, mudanza.codigo_postal_destino)
        tipo = f"{zona_origen} a {zona_destino}"

        # 2. Lógica de Tarifas por KM
        if zona_origen == 'CABA' and zona_destino == 'CABA': tarifa_km = 30000
        elif zona_origen == 'CABA' and zona_destino == 'PROVINCIA': tarifa_km = 35000
        elif zona_origen == 'PROVINCIA' and zona_destino == 'CABA': tarifa_km = 32000
        elif zona_origen == 'PROVINCIA' and zona_destino == 'PROVINCIA': tarifa_km = 25000
        else: tarifa_km = 20000 # Larga distancia al interior

        costo_distancia = tarifa_km * distancia

        # 3. Costo Operarios según tamaño de mudanza
        if mudanza.tamano == 'PEQUENA': costo_ope = 20000
        elif mudanza.tamano == 'MEDIANA': costo_ope = 40000
        else: costo_ope = 65000 # GRANDE

        # 4. Extras Premium
        costo_prem = 50000 if mudanza.solicita_servicio_premium else 0

        # Total
        total = costo_distancia + costo_ope + costo_prem

        # Pre-cargamos el formulario con los cálculos
        initial_data = {
            'fecha_propuesta': mudanza.fecha_mudanza,
            'distancia_km': round(distancia, 2),
            'tipo_viaje': tipo,
            'costo_distancia': round(costo_distancia, 2),
            'costo_operarios': round(costo_ope, 2),
            'costo_premium': round(costo_prem, 2),
            'cargos_extra': 0, # Agregamos esto
            'precio': round(total, 2)
        }
        form = CotizacionForm(instance=mudanza, initial=initial_data)
        
    return render(request, 'core/cotizar_mudanza.html', {'form': form, 'mudanza': mudanza})


@login_required
def aceptar_cotizacion(request, mudanza_id):
    # El cliente acepta el precio y fecha
    mudanza = get_object_or_404(Mudanza, id=mudanza_id, cliente=request.user, estado='COTIZADA')
    mudanza.estado = 'ASIGNADA'
    mudanza.save()
    return redirect('panel_cliente')

@login_required
def finalizar_mudanza(request, mudanza_id):
    # Solo la empresa asignada puede finalizar un viaje que está EN CURSO (ASIGNADA)
    mudanza = get_object_or_404(Mudanza, id=mudanza_id, empresa=request.user, estado='ASIGNADA')
    mudanza.estado = 'FINALIZADA'
    mudanza.save()
    return redirect('panel_empresa')

@login_required
def dejar_resena(request, mudanza_id):
    # Buscamos la mudanza que esté FINALIZADA y pertenezca al usuario
    mudanza = get_object_or_404(Mudanza, id=mudanza_id, cliente=request.user, estado='FINALIZADA')
    
    # Seguridad: Si ya tiene reseña, lo rebotamos al panel
    if mudanza.tiene_resena:
        return redirect('panel_cliente')
        
    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.mudanza = mudanza
            resena.cliente = request.user
            resena.empresa = mudanza.empresa
            resena.save()
            
            # Le avisamos a la mudanza que ya fue calificada
            mudanza.tiene_resena = True
            mudanza.save()
            
            return redirect('panel_cliente')
    else:
        form = ResenaForm()
        
    return render(request, 'core/dejar_resena.html', {'form': form, 'mudanza': mudanza})