from django import forms
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from models import RolProyecto

from django.forms import ModelMultipleChoiceField


class MyModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.codename


class RolProyectoCreateForm(forms.ModelForm):
    permissions = MyModelMultipleChoiceField(Permission.objects.exclude(
        Q(content_type__app_label='contenttypes') |
        Q(content_type__app_label='admin') |
        Q(content_type__app_label='sessions') |
        Q(content_type__app_label='usuarios') |
        Q(content_type__app_label='roles_proyecto') |
        Q(content_type__app_label='auth') |
        Q(content_type__app_label='clientes') |
        Q(content_type__model='historialuserstory')
        ),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'checkbox1'}),
        help_text="Debe seleccionar al menos un permiso.",)

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create Group and GroupProfile without database save")
        rol = super(RolProyectoCreateForm, self).save(commit=True)
        group_profile = RolProyecto(group=rol, es_rol_proyecto=True)

        group_profile.save()
        return rol, group_profile
        

class RolProyectoUpdateForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ['name']


class RolProyectoPermisosForm(forms.ModelForm):

    permissions = MyModelMultipleChoiceField(Permission.objects.exclude(
        Q(content_type__app_label='contenttypes') |
        Q(content_type__app_label='admin') |
        Q(content_type__app_label='sessions') |
        Q(content_type__app_label='usuarios') |
        Q(content_type__app_label='roles_proyecto') |
        Q(content_type__app_label='auth') |
        Q(content_type__app_label='clientes') |
        Q(content_type__model='historialuserstory')
        ),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'checkbox1'}),
        help_text="Debe seleccionar al menos un permiso.",)

    class Meta:
        model = Group
        fields = ['permissions']
