from django import forms

from models import UserStory, HistorialUserStory
from apps.proyectos.models import Proyecto


class UserStoryCreateForm(forms.ModelForm):
    def __init__(self, user, **kwargs):
        super(UserStoryCreateForm, self).__init__(**kwargs)
        self.user = user

    valor_negocio = forms.IntegerField(required=True, min_value=0, max_value=10, initial=0)

    class Meta:
        model = UserStory
        fields = ['nombre', 'descripcion', 'valor_negocio']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create UserStory without database save")
        #userStory = super(UserStoryCreateForm, self).save(commit=True)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        userStory = UserStory.objects.create(nombre=self.cleaned_data['nombre'],
                                             descripcion=self.cleaned_data['descripcion'],
                                             valor_negocio=self.cleaned_data['valor_negocio'],
                                             proyecto=proyecto)
        print userStory
        print proyecto

        #userStory.proyecto = self.cleaned_data['proyecto']
        #print self.cleaned_data['proyecto']
        userStory.save()
        print userStory

        historial_us = HistorialUserStory(user_story=userStory, operacion='creado', usuario=self.user)
        historial_us.save()

        #print "nombre %s" % self.cleaned_data['nombre']
        return proyecto


class UserStoryUpdateFormPO(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(UserStoryUpdateFormPO, self).__init__(*args, **kwargs)
        self.user = user

        #roles = kwargs['initial']['rolproyecto']
        user_story_string = kwargs['initial']['user_story']
        kwargs.pop('initial')

        user_story = UserStory.objects.get(pk=user_story_string.pk)

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['nombre'] = forms.CharField(required=True)
        self.fields['descripcion'] = forms.CharField(required=True)
        self.fields['valor_negocio'] = forms.IntegerField(required=True, min_value=0, max_value=10)

        self.fields['id'].initial = user_story.id
        self.fields['nombre'].initial = user_story.nombre
        self.fields['descripcion'].initial = user_story.descripcion
        self.fields['valor_negocio'].initial = user_story.valor_negocio

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        cleaned_data = super(UserStoryUpdateFormPO, self).clean()
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        proyecto = super(UserStoryUpdateFormPO, self).save(commit=True)
        user_story = UserStory.objects.get(pk=self.cleaned_data['id'])

        if user_story.nombre != cleaned_data['nombre']:
            user_story.nombre = self.cleaned_data['nombre']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="nombre",
                                              valor=self.cleaned_data['nombre'], usuario=self.user)
            historial_us.save()
            print 'cambio el nombre %s ' % user_story.nombre
        if user_story.descripcion != cleaned_data['descripcion']:
            user_story.descripcion = self.cleaned_data['descripcion']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="descripcion",
                                              valor=self.cleaned_data['descripcion'], usuario=self.user)
            historial_us.save()
            print 'cambio la descripcion antes: %s - ahora: %s' % (user_story.descripcion, cleaned_data['descripcion'])
        if user_story.valor_negocio != cleaned_data['valor_negocio']:
            user_story.valor_negocio = self.cleaned_data['valor_negocio']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="valor de negocio",
                                              valor=self.cleaned_data['valor_negocio'], usuario=self.user)
            historial_us.save()
            print 'cambio el valor de negocio %s ' % user_story.valor_negocio

        user_story.save()

        return proyecto


class UserStoryUpdateFormSM(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(UserStoryUpdateFormSM, self).__init__(*args, **kwargs)
        self.user = user

        user_story_string = kwargs['initial']['user_story']
        kwargs.pop('initial')

        user_story = UserStory.objects.get(pk=user_story_string.pk)

        ESTADO_USER_STORY=(
        ('No asignado', 'No asignado'),
        ('Activo', 'Activo'),
        ('Pendiente', 'Pendiente'),
        ('Finalizado', 'Finalizado'),
        ('Aprobado', 'Aprobado'),
        ('Descartado', 'Descartado'),
        )

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())
        self.fields['prioridad'] = forms.IntegerField(required=True, min_value=0, max_value=10)
        self.fields['valor_tecnico'] = forms.IntegerField(required=True, min_value=0, max_value=10)
        self.fields['estimacion'] = forms.IntegerField(required=True, min_value=0, max_value=240,
                                                       help_text='En horas. Maximo 240 horas.')
        #self.fields['flujo'] = forms.ModelChoiceField(Flujo.objects.all(), required=True)

        self.fields['id'].initial = user_story.id
        self.fields['prioridad'].initial = user_story.prioridad
        self.fields['valor_tecnico'].initial = user_story.valor_tecnico
        self.fields['estimacion'].initial = user_story.estimacion
        #self.fields['flujo'].initial = user_story.flujo
        print user_story.prioridad
        print "prioridad initial = %s" % self.fields['prioridad'].initial
        print "valor_tecnico initial = %s" % self.fields['valor_tecnico'].initial

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        cleaned_data = super(UserStoryUpdateFormSM, self).clean()
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        proyecto = super(UserStoryUpdateFormSM, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['id'])

        if user_story.usuario is None:
            user_story.estado = 'No asignado'
        elif user_story.usuario is not None:
            if str(user_story.estado) == 'Finalizado' or str(user_story.estado) == 'Aprobado':
                pass
            else:
                user_story.estado = 'Activo'

        if user_story.prioridad != cleaned_data['prioridad']:
            user_story.prioridad = self.cleaned_data['prioridad']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="prioridad",
                                              valor=self.cleaned_data['prioridad'], usuario=self.user)
            historial_us.save()

        if user_story.valor_tecnico != cleaned_data['valor_tecnico']:
            user_story.valor_tecnico = self.cleaned_data['valor_tecnico']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="valor tecnico",
                                              valor=self.cleaned_data['valor_tecnico'], usuario=self.user)
            historial_us.save()

        if user_story.estimacion != cleaned_data['estimacion']:
            user_story.estimacion = self.cleaned_data['estimacion']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="estimacion",
                                              valor=self.cleaned_data['estimacion'], usuario=self.user)
            historial_us.save()

        #if user_story.flujo != cleaned_data['flujo']:
        #    user_story.flujo = self.cleaned_data['flujo']
        #    historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="flujo",
        #                                      valor=self.cleaned_data['flujo'], usuario=self.user)
        #    historial_us.save()

        user_story.save()

        return proyecto