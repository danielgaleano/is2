from django import forms
from django.forms import ModelMultipleChoiceField

from models import Flujo, Actividad, Estado, PlantillaFlujo, ActividadFlujo
from apps.proyectos.models import Proyecto


class MyModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s -- orden: %d" % (obj.nombre, obj.orden)


class FlujoCreateForm(forms.ModelForm):
    actividades = ModelMultipleChoiceField(Actividad.objects.all(),
            widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = Flujo
        fields = [ 'nombre', 'actividades']


class PlantillaFlujoCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        lista = kwargs.pop('lista', None)
        print "en forms %s" % lista
        super(PlantillaFlujoCreateForm, self).__init__(*args, **kwargs)
        self.fields['actividades'] = forms.ModelMultipleChoiceField(ActividadFlujo.objects.all(),
                                                                    widget=forms.HiddenInput(), required=False)

        print "antes %s" % self.fields['actividades']
        if lista:

            dic = {}
            for arr in lista:
                dic[arr.pk] = arr

            self.fields['actividades'].initial = dic

    #actividades = MyModelMultipleChoiceField(Actividad.objects.all(),
    #                                         widget=forms.CheckboxSelectMultiple, required=True)
    
    class Meta:
        model = PlantillaFlujo
        fields = ['nombre']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create PlantillaFlujo without database save")

        plantilla_flujo = super(PlantillaFlujoCreateForm, self).save(commit=True)

        for actividad in self.cleaned_data['actividades']:
            print actividad
            plantilla_flujo.actividades.add(actividad)

        plantilla_flujo.save()

        return plantilla_flujo


class PlantillaFlujoUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        context = super(PlantillaFlujoUpdateForm, self).__init__(*args, **kwargs)
        plantilla_flujo = PlantillaFlujo.objects.get(pk=kwargs['instance'].pk)
        #print miembros_actuales
        # lista = User.objects.exclude(Q(is_staff=True) | Q(id__in=miembros_actuales))
        # print lista
        # for usuario in User.objects.all():
        #   for miembro in miembros_actuales:
        #       if usuario !=
        # lista_sin_actuales = Proyecto.objects.exclude(equipo=miembros_actuales)
        self.fields['nombre'].initial = plantilla_flujo.nombre
        #print "hola"
        #print self.fields['usuario']
        # self.fields['usuario'].initial = lista_sin_actuales
    #actividades = MyModelMultipleChoiceField(Actividad.objects.all(),
    #                                         widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = PlantillaFlujo
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


class AsignarFlujoProyectoForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(AsignarFlujoProyectoForm, self).__init__(*args, **kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['instance'].pk)
        flujos_actuales = Flujo.objects.filter(proyecto=proyecto)

        #self.fields['usuario'] = forms.ModelChoiceField(User.objects.exclude(Q(is_staff=True) | Q(id__in=miembros_actuales)), required=True)
        self.fields['flujos'] = forms.ModelMultipleChoiceField(Flujo.objects.all().order_by('id'),
                                                               widget=forms.CheckboxSelectMultiple, required=True)

        dic = {}
        for arr in flujos_actuales:
            dic[arr.pk] = arr
        self.fields['flujos'].initial = dic

    #groups = forms.ModelMultipleChoiceField(Group.objects.all().filter(rolproyecto__es_rol_proyecto=None),
                                            #widget=forms.CheckboxSelectMultiple, required=False)

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)
    #flujos = forms.ModelMultipleChoiceField(Flujo.objects.filter(proyecto=proyecto).exclude(name='Scrum Master'),
            #widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create Flujo without database save")

        proyecto = super(AsignarFlujoProyectoForm, self).save(commit=True)

        lista_completa = Flujo.objects.all()
        print "self %s" % self.cleaned_data['flujos']
        for flujo in self.cleaned_data['flujos']:
            flujo.proyecto = proyecto
            flujo.save()
            for f in lista_completa:
                if f not in self.cleaned_data['flujos']:
                    f.proyecto = None
                    f.save()

        return proyecto