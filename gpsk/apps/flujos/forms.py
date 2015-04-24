from django import forms
from models import Flujo, Actividad, Estado

from django.forms import ModelMultipleChoiceField


class MyModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s -- orden: %d" % (obj.nombre, obj.orden)


class FlujoCreateForm(forms.ModelForm):
    #actividades = MyModelMultipleChoiceField(Actividad.objects.all(),
    #                                         widget=forms.CheckboxSelectMultiple, required=True)
    
    class Meta:
        model = Flujo
        fields = ['nombre']


class ActividadCreateForm(forms.ModelForm):
    
    class Meta:
        model = Actividad
        fields = ['nombre']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create Actividad without database save")
        actividad = super(ActividadCreateForm, self).save(commit=True)

        estado1 = Estado(nombre="To do")
        estado1.save()
        estado2 = Estado(nombre="Doing")
        estado2.save()
        estado3 = Estado(nombre="Done")
        estado3.save()

        actividad.estados.add(estado1)
        actividad.estados.add(estado2)
        actividad.estados.add(estado3)

        actividad.save()

        return actividad