from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from models import Usuario
from views import *
from django.contrib.auth.forms import AdminPasswordChangeForm


class UserCreateForm(UserCreationForm):
    """
    Clase que contiene los campos del formulario, necesarios para el registro de nuevos Usuarios
    en la base de datos.

    @type UserCreationForm: django.contrib.auth.forms
    @ivar UserCreationForm: Se hereda el formulario incorporado en django para la creacion
                            del objeto User, para usar sus funcionalidades
    """
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    password1 = forms.RegexField(label='Password', regex=r'^[\w.@+-]+$', min_length=5,
                                 widget=forms.PasswordInput,
                                 help_text='Minimo 5 carateres. Letras, digitos y @/./+/-/_ solamente.')
    password2 = forms.RegexField(label='Password (Confirmacion)', regex=r'^[\w.@+-]+$', min_length=5,
                                 widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    telefono = forms.RegexField(regex=r'^[\d()+-]+$', max_length=20,
                                help_text='Digitos y + - ( ) solamente.')
    direccion = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email']

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
    @ivar forms.ModelForm: Se hereda el formulario incorporado en django para los modelos
                            para usar sus funcionalidades
    """
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        eluser = Usuario.objects.get(user=kwargs['instance'].pk)

        telefono = eluser.telefono
        direccion = eluser.direccion

        self.fields['telefono'].initial = telefono
        self.fields['direccion'].initial = direccion

    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True)
    telefono = forms.RegexField(regex=r'^[\d()+-]+$', max_length=20,
                                help_text='Digitos y + - ( ) solamente.')
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


class UserAsignarRolesForm(forms.ModelForm):

    groups = forms.ModelMultipleChoiceField(Group.objects.all().filter(rolproyecto__es_rol_proyecto=None),
                                            widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = User
        fields = ['groups']


class MyPasswordChangeForm(AdminPasswordChangeForm):
    error_messages = {
        'password_too_short': ("El password debe tener al menos 5 carateres."),
        'password_mismatch': ("Los dos campos de password no coinciden."),
        }

    def clean_password1(self):
        passwd = self.cleaned_data['password1']
        if passwd and len(passwd) < 5:
            raise forms.ValidationError(
                self.error_messages['password_too_short'],
                code='password_too_short',
            )
        return passwd