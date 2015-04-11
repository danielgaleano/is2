from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


class UserProfileForm(forms.ModelForm):
    """
    Clase que contiene los campos del formulario, necesarios para la modificacion del perfil del usuario
    registrado en la base de datos.

    @type forms.ModelForm: django.forms
    @ivar forms.ModelForm: Se hereda el formulario incorporado en django para los modelos
                            para usar sus funcionalidades
    """

    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True)


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Password antiguo", widget=forms.PasswordInput)
    new_password1 = forms.RegexField(label="Password nuevo", regex=r'^[\w.@+-]+$', min_length=5,
                                     widget=forms.PasswordInput,
                                     help_text='Minimo 5 carateres. Letras, digitos y @/./+/-/_ solamente.')
    new_password2 = forms.RegexField(label="Password nuevo (confirmacion)", regex=r'^[\w.@+-]+$', min_length=5,
                                     widget=forms.PasswordInput)