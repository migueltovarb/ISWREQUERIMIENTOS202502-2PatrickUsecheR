from django.db import models
from django.contrib.auth.forms import UserCreationForm
import uuid
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class reclamo(models.Model):
    ESTADOS = [
        ('Pendiente por atender', 'Pendiente por atender'),
        ('En atención','En atención'),
        ('Atendido','Atendido'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=8, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.IntegerField()
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=40, choices=ESTADOS, default='Pendiente por atender')
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)
    

class solicitud(models.Model):
    ESTADOS = [
        ('Pendiente por atender', 'Pendiente por atender'),
        ('En atención','En atención'),
        ('Atendido','Atendido'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=8, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.IntegerField()
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=40, choices=ESTADOS, default='Pendiente por atender')
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)