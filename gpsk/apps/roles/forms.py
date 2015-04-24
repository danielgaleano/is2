from django import forms
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from django.forms import ModelMultipleChoiceField


class MyModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.codename


class RolCreateForm(forms.ModelForm):

    permissions = MyModelMultipleChoiceField(Permission.objects.exclude(
        Q(content_type__app_label='contenttypes') |
        Q(content_type__app_label='admin') |
        Q(content_type__app_label='sessions') |
        Q(content_type__model='permission') |
        Q(content_type__model='user') |
        Q(content_type__app_label='user_stories')),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'checkbox1'}),
        )

    class Meta:
        model = Group
        fields = ['name', 'permissions']


class RolUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Group
        fields = ['name']


class RolAsignarPermisosForm(forms.ModelForm):

    permissions = MyModelMultipleChoiceField(Permission.objects.exclude(
        Q(content_type__app_label='contenttypes') |
        Q(content_type__app_label='admin') |
        Q(content_type__app_label='sessions') |
        Q(content_type__model='permission') |
        Q(content_type__model='user') |
        Q(content_type__app_label='user_stories')),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'checkbox1'}),
        help_text="Debe seleccionar al menos un permiso.",)

    class Meta:
        model = Group
        fields = ['permissions']