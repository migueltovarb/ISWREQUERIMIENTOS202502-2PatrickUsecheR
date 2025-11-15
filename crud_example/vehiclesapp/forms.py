from django import forms
from .models import vehiculo

class vehiculoForm(forms.ModelForm):
    class Meta:
        model = vehiculo
        fields = [
            'placa',
            'marca',
            'color',
            'modelo',
        ]
        
        labels = {
            'placa' : 'Número de placa',
            'marca' : 'Marca del vehículo',
            'modelo' : 'Modelo del vehículo',
            'color' : 'Color del vehículo',
        }
        
        widgets = {
            'placa': forms.TextInput(attrs={'class':'form-control'}),
            'marca': forms.TextInput(attrs={'class':'form-control'}),
            'modelo': forms.TextInput(attrs={'class':'form-control'}),
            'color': forms.Select(attrs={'class':'form-control'}),
        }