from django import forms
from .models import reclamo, solicitud
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import uuid

class reclamoForm(forms.ModelForm):
    class Meta:
        model = reclamo
        fields = [
            'nombre',
            'email',
            'telefono',
            'descripcion',
        ]
        
        labels = {
            'nombre' : 'Nombre',
            'email' : 'Email',
            'telefono' : 'Telefono',
            'descripcion' : 'descripción',
        }
        
        widgets = {
            'nombre' : forms.TextInput(attrs={'class' : 'form-control'}),
            'email' : forms.EmailInput(attrs={'class' : 'form-control'}),
            'telefono' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'descripcion' : forms.Textarea(attrs={'class' : 'form-control'}),
        }
        
    
class solicitudForm(forms.ModelForm):
    class Meta:
        model = solicitud
        fields = [
            'nombre',
            'email',
            'telefono',
            'descripcion',
        ]
        
        labels = {
            'nombre' : 'Nombre',
            'email' : 'Email',
            'telefono' : 'Telefono',
            'descripcion' : 'Descripción',
        }
        
        widgets = {
            'nombre' : forms.TextInput(attrs={'class' : 'form-control'}),
            'email' : forms.EmailInput(attrs={'class' : 'form-control'}),
            'telefono' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'descripcion' : forms.Textarea(attrs={'class' : 'form-control'}),
        }
        
        
class CustomUserCreationForm(UserCreationForm):

    # Campo visible (puede repetirse)
    full_name = forms.CharField(
        required=True,
        label="Nombre Completo:",
        error_messages={'required': 'Por favor ingresa tu nombre completo.'}
    )

    # username oculto para que tu template no lo muestre
    username = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    email = forms.EmailField(
        required=True,
        label="Correo Electrónico:",
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingresa un correo válido.'
        }
    )

    password1 = forms.CharField(
        label="Contraseña:",
        widget=forms.PasswordInput,
        error_messages={'required': 'Ingresa una contraseña.'}
    )

    password2 = forms.CharField(
        label="Confirmar Contraseña:",
        widget=forms.PasswordInput,
        error_messages={'required': 'Confirma tu contraseña.'}
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)

        # Guardamos el nombre completo en first_name
        user.first_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']

        # Generamos username único automático
        user.username = uuid.uuid4().hex[:30]

        if commit:
            user.save()
        return user
    
    
class BuscarCodigoForm(forms.Form):
    codigo = forms.CharField(label='Codigo del reclamo/solicitud:', max_length=12)
    
class UsuarioEmailChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.email
    
class CambiarGrupoForm(forms.Form):
    usuario = UsuarioEmailChoiceField(
        queryset=User.objects.all(),
        label = 'Usuario:'
    )
    
    rol_actual = forms.CharField(
        label='Rol actual:',
        required=False,
        disabled=True
    )
    nuevo_rol =forms.ChoiceField(
        label='Nuevo rol:',
        choices=[
            ('Empleado', 'Empleado'),
            ('Administradores', 'Administradores'),
            ('Cliente', 'Cliente')
        ]
    )
    
    
class CambiarEstadoForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=[('reclamo', 'Reclamo'), ('solicitud', 'Solicitud')],
        widget=forms.HiddenInput()
    )
    codigo = forms.CharField(
        max_length=12,
        label="Código del reclamo/solicitud",
        widget=forms.TextInput(attrs={'readonly':'readonly'})
    )
    nuevo_estado = forms.ChoiceField(
        choices=[
            ('Pendiente por atender', 'Pendiente por atender'),
            ('En atención','En atención'),
            ('Atendido','Atendido')
        ],
        label="Nuevo Estado"
    )