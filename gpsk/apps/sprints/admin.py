from django.contrib import admin
from db_file_storage.form_widgets import DBAdminClearableFileInput
from django import forms

from models import Sprint
from apps.user_stories.models import Adjunto


class AgregarAdjuntoForm(forms.ModelForm):
    class Meta:
        model = Adjunto
        exclude = []
        widgets = {
            'archivo': DBAdminClearableFileInput
        }


class AdjuntoAdmin(admin.ModelAdmin):
    form = AgregarAdjuntoForm


admin.site.register(Sprint)
admin.site.register(Adjunto, AdjuntoAdmin)
