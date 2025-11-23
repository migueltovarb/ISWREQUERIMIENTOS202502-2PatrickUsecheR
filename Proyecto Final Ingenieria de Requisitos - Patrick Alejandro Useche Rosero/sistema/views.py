from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect 
from .models import reclamo, solicitud
from .forms import reclamoForm, solicitudForm, CustomUserCreationForm, User, BuscarCodigoForm, CambiarGrupoForm, CambiarEstadoForm
from django.contrib.auth import authenticate, login, logout
import uuid
from functools import wraps
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import enviar_notificacion_estado
# Create your views here.
def acceso_grupos(grupos_permitidos=[]):
    
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_groups = list(request.user.groups.values_list('name', flat=True))
            
            if not user_groups and 'sin_grupo' in grupos_permitidos:
                return view_func(request, *args, **kwargs)
            
            if set(user_groups).intersection(grupos_permitidos):
                return view_func(request, *args, **kwargs)
            
            return redirect('/')
        
        return _wrapped_view
    return decorator


def home(request):
    user_rol = None
    if request.user.is_authenticated:
        grupos = request.user.groups.values_list('name', flat=True)
        if 'Empleado' in grupos:
            user_rol = 'Empleado'
        elif 'Administradores' in grupos:
            user_rol = 'Administradores'
        else:
            user_rol = 'Cliente'
    return render(request, 'base.html', {
        'user_rol' : user_rol
    })

def registrarse(request):
    if request.method == "GET":
        return render(request, "registrarse.html", {
            "form": CustomUserCreationForm()
        })
    
    form = CustomUserCreationForm(request.POST)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/")

    return render(request, "registrarse.html", {
        "form": form,
        "error": "Revisa los datos, algo falló."
    })
    

def iniciar_sesion(request):
    if request.method == 'GET':
        return render(request, 'iniciar_sesion.html')
    email = request.POST.get("email")
    password = request.POST.get("password")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return render(request, 'iniciar_sesion.html', {
            'error' : 'El correo no esta registrado.'
        })
        
    user = authenticate(username=user.username, password=password)
    
    if user is None:
        return render(request, 'iniciar_sesion.html',{
            'error' : 'Contraseña incorrecta.'
        })
        
    login(request, user)
    return HttpResponseRedirect('/')
    
def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@acceso_grupos(grupos_permitidos=['sin_grupo'])
def registrar_reclamo(request):
    form = reclamoForm(request.POST or None)

    if form.is_valid():
        reclamo_obj = form.save(commit=False)
        reclamo_obj.usuario = request.user
        reclamo_obj.estado = 'Pendiente por atender'
        if not reclamo_obj.codigo:
            reclamo_obj.codigo = uuid.uuid4().hex[:12].upper()

        reclamo_obj.save()

        # Mensaje final o redirección elegante
        return render(request, "reclamo_exito.html", {
            "codigo": reclamo_obj.codigo
        })

    return render(request, "registrar_reclamo.html", {
        "form": form
    })

@acceso_grupos(grupos_permitidos=['sin_grupo'])
def registrar_solicitud(request):
    form = solicitudForm(request.POST or None)

    if form.is_valid():
        solicitud_obj = form.save(commit=False)
        solicitud_obj.usuario = request.user
        # Estado por defecto
        solicitud_obj.estado = 'Pendiente por atender'

        # Código único si el modelo lo usa
        if not solicitud_obj.codigo:
            solicitud_obj.codigo = uuid.uuid4().hex[:12].upper()

        solicitud_obj.save()

        # Mensaje final o redirección elegante
        return render(request, "solicitud_exito.html", {
            "codigo": solicitud_obj.codigo
        })

    return render(request, "registrar_solicitud.html", {
        "form": form
    })
    
@acceso_grupos(grupos_permitidos=['sin_grupo'])
def realizar_seguimiento(request):
    resultado_reclamo = None
    resultado_solicitud = None
    mensaje = ''
    form = BuscarCodigoForm(request.POST or None)  # usa la clase correcta
    
    if request.method == 'POST' and form.is_valid():  # no olvides los paréntesis
        codigo = form.cleaned_data['codigo']
        
        # Buscar reclamo
        try:
            reclamo_obj = reclamo.objects.get(codigo__iexact=codigo)
            if reclamo_obj.usuario == request.user:
                resultado_reclamo = reclamo_obj
            else:
                mensaje += 'El reclamo con ese código no pertenece a tu cuenta. '
        except reclamo.DoesNotExist:
            pass
        
        # Buscar solicitud
        try:
            solicitud_obj = solicitud.objects.get(codigo__iexact=codigo)
            if solicitud_obj.usuario == request.user:
                resultado_solicitud = solicitud_obj
            else:
                mensaje += 'La solicitud con ese código no pertenece a tu cuenta.'
        except solicitud.DoesNotExist:
            if not resultado_reclamo:
                mensaje = 'No se encontró ningún reclamo ni solicitud con ese código.'

    return render(request, 'seguimiento_estado.html', {
        'form': form,
        'resultado_reclamo': resultado_reclamo,
        'resultado_solicitud': resultado_solicitud,
        'mensaje': mensaje
    })
    
@acceso_grupos(grupos_permitidos=['sin_grupo'])
def visualizar_reclamos(request):
    reclamos = reclamo.objects.filter(usuario=request.user).order_by('-fecha_registro')
    return render(request, 'visualizar_reclamos.html', {'reclamos' : reclamos})

@acceso_grupos(grupos_permitidos=['sin_grupo'])
def visualizar_solicitudes(request):
    solicitudes = solicitud.objects.filter(usuario=request.user)
    return render(request, "visualizar_solicitudes.html", {
        "solicitudes": solicitudes
        })

def es_empleado_o_admin(user):
    return user.groups.filter(name__in=['Empleado','Administradores']).exists()

@login_required
@user_passes_test(es_empleado_o_admin)
def cambiar_estado(request):
    mensaje = ''
    
    if request.method == "POST":
        codigo = request.POST.get("codigo")
        tipo = request.POST.get("tipo")  # 'reclamo' o 'solicitud'
        nuevo_estado = request.POST.get("nuevo_estado")

        if tipo == "reclamo":
            obj = reclamo.objects.get(codigo=codigo)
            obj.estado = nuevo_estado
            obj.save()
            enviar_notificacion_estado(obj.email, "Reclamo", obj.codigo, obj.estado)
            mensaje = f"El estado del reclamo {obj.codigo} se actualizó a '{nuevo_estado}'."

        elif tipo == "solicitud":
            obj = solicitud.objects.get(codigo=codigo)
            obj.estado = nuevo_estado
            obj.save()
            enviar_notificacion_estado(obj.email, "Solicitud", obj.codigo, obj.estado)
            mensaje = f"El estado de la solicitud {obj.codigo} se actualizó a '{nuevo_estado}'."

    # Traer todos los reclamos y solicitudes para mostrar en la tabla
    reclamos = reclamo.objects.all().order_by('-fecha_registro')
    solicitudes = solicitud.objects.all().order_by('-fecha_registro')

    return render(request, "cambiar_estado.html", {
        'reclamos': reclamos,
        'solicitudes': solicitudes,
        'mensaje': mensaje
    })
@acceso_grupos(grupos_permitidos=['Administradores'])
def gestionar_permisos(request):
    mensaje = ''
    form = CambiarGrupoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        usuario = form.cleaned_data['usuario']
        nuevo_rol = form.cleaned_data['nuevo_rol']

        # Aquí va la lógica para cambiar el grupo
        usuario.groups.clear()  # elimina los grupos anteriores
        if nuevo_rol != 'Cliente':  # Cliente = sin grupo
            from django.contrib.auth.models import Group
            grupo = Group.objects.get(name=nuevo_rol)
            usuario.groups.add(grupo)

        # Usar el nombre completo en el mensaje
        nombre_usuario = getattr(usuario, 'nombre', usuario.get_full_name() or usuario.email)
        mensaje = f"Permisos de {nombre_usuario} actualizados correctamente."

    return render(request, "gestionar_permisos.html", {
        'form': form,
        'mensaje': mensaje
    })
    

@acceso_grupos(grupos_permitidos=['Administradores'])
def obtener_rol_actual(request):
    usuario_id = request.GET.get('usuario_id')
    try:
        usuario = User.objects.get(id=usuario_id)
        grupos = usuario.groups.values_list('name', flat=True)
        if grupos:
            rol_actual = ', '.join(grupos)
        else:
            rol_actual = 'Cliente'
        return JsonResponse({'rol_actual': rol_actual})
    except User.DoesNotExist:
        return JsonResponse({'rol_actual': 'Desconocido'})