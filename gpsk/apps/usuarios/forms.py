from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from models import Usuario
from views import *


class UserCreateForm(UserCreationForm):
    """
    Clase que contiene los campos del formulario, necesarios para el registro de nuevos Usuarios
    en la base de datos.

    @type UserCreationForm: django.contrib.auth.forms
    @param UserCreationForm: Se hereda el formulario incorporado en django para la creacion
                            del objeto User, para usar sus funcionalidades
    """
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=20)
    direccion = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("No se puede crear User y Usuario sin guardar en la base de datos")
        user = super(UserCreateForm, self).save(commit=True)
        user_profile = Usuario(user=user, telefono=self.cleaned_data['telefono'],
                               direccion=self.cleaned_data['direccion'])
        user_profile.save()
        return user, user_profile


class UserUpdateForm(forms.ModelForm):
    """
    Clase que contiene los campos del formulario, necesarios para la modificacion de Usuarios
    registrados en la base de datos.

    @type forms.ModelForm: django.forms
    @param forms.ModelForm: Se hereda el formulario incorporado en django para los modelos
                            para usar sus funcionalidades
    """
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        eluser = Usuario.objects.get(user=kwargs['instance'].pk)

        telefono = eluser.telefono
        direccion = eluser.direccion

        self.fields['telefono'].initial = telefono
        self.fields['direccion'].initial = direccion

    telefono = forms.CharField(max_length=20)
    direccion = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        usuario = Usuario.objects.get(user=self.instance)
        user = super(UserUpdateForm, self).save(commit=True)
        usuario.telefono = self.cleaned_data['telefono']
        usuario.direccion = self.cleaned_data['direccion']
        usuario.save()
        return user, usuario
