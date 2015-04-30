from django import forms

from models import UserStory, HistorialUserStory
from apps.proyectos.models import Proyecto


class UserStoryCreateForm(forms.ModelForm):
    def __init__(self, user, **kwargs):
        super(UserStoryCreateForm, self).__init__(**kwargs)
        self.user = user

    valor_negocio = forms.IntegerField(required=True, min_value=0, max_value=10)

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

        #self.fields['rolproyecto'] = forms.ModelMultipleChoiceField(Group.objects.all().filter(rolproyecto__es_rol_proyecto=True).exclude(name='Scrum Master'),
        #        widget=forms.CheckboxSelectMultiple, required=False)

        #dic = {}
        #for arr in roles:
        #    dic[arr.pk] = arr
        #self.fields['rolproyecto'].initial = dic

        user_story = UserStory.objects.get(pk=user_story_string.pk)

        #self.fields['usuario'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['nombre'] = forms.CharField(required=True)
        self.fields['descripcion'] = forms.CharField(required=True)
        self.fields['valor_negocio'] = forms.IntegerField(required=True, min_value=0, max_value=10)

        #self.fields['usuario'].initial = user
        self.fields['id'].initial = user_story.id
        self.fields['nombre'].initial = user_story.nombre
        self.fields['descripcion'].initial = user_story.descripcion
        self.fields['valor_negocio'].initial = user_story.valor_negocio

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    #def clean(self):
    #    cleaned_data =super(UserStoryUpdateFormPO, self).clean()
    #    user_story = UserStory.objects.get(pk=self.cleaned_data['id'])
    #    if user_story.nombre != cleaned_data['nombre']:
    #        print 'cambio el nombre %s ' % user_story.nombre

    #    return cleaned_data

    def save(self, commit=True):
        cleaned_data = super(UserStoryUpdateFormPO, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        proyecto = super(UserStoryUpdateFormPO, self).save(commit=True)
        #user_story = UserStory.objects.get(pk=self.context[''])
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

        #user_story.nombre = self.cleaned_data['nombre']
        #user_story.descripcion = self.cleaned_data['descripcion']
        #user_story.valor_negocio = self.cleaned_data['valor_negocio']
        user_story.save()

        return proyecto


class UserStoryUpdateFormSM(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(UserStoryUpdateFormSM, self).__init__(*args, **kwargs)
        self.user = user
        miembros_actuales = Proyecto.objects.get(pk=kwargs['instance'].pk).equipo.all()

        #roles = kwargs['initial']['rolproyecto']
        user_story_string = kwargs['initial']['user_story']
        kwargs.pop('initial')

        #self.fields['rolproyecto'] = forms.ModelMultipleChoiceField(Group.objects.all().filter(rolproyecto__es_rol_proyecto=True).exclude(name='Scrum Master'),
        #        widget=forms.CheckboxSelectMultiple, required=False)

        #dic = {}
        #for arr in roles:
        #    dic[arr.pk] = arr
        #self.fields['rolproyecto'].initial = dic

        user_story = UserStory.objects.get(pk=user_story_string.pk)

        ESTADO_USER_STORY=(
        ('No asignado', 'No asignado'),
        ('Activo', 'Activo'),
        ('Pendiente', 'Pendiente'),
        ('Finalizado', 'Finalizado'),
        ('Aprobado', 'Aprobado'),
        ('Descartado', 'Descartado'),
        )
        #self.fields['usuario'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())
        self.fields['prioridad'] = forms.IntegerField(required=True, min_value=0, max_value=10)
        self.fields['valor_tecnico'] = forms.IntegerField(required=True, min_value=0, max_value=10)
        self.fields['estimacion'] = forms.IntegerField(required=True, min_value=0, max_value=240,
                                                       help_text='En horas. Maximo 240 horas.')
        #self.fields['usuario'] = forms.ModelChoiceField(Proyecto.objects.get(pk=kwargs['instance'].pk).equipo.all(),
        #                                               required=False)
        #self.fields['estado'] = forms.ChoiceField(choices=ESTADO_USER_STORY, widget=forms.HiddenInput())
        #flitrar solo los flujos del proyecto
        #self.fields['flujo'] = forms.ModelChoiceField(Flujo.objects.all(), required=False)
        #flitrar solo los sprints del proyecto
        #self.fields['sprint'] = forms.ModelChoiceField(Sprint.objects.filter(proyecto=kwargs['instance'].pk).order_by('pk'),
        #                                               required=False)

        #if str(user_story.estado) == 'Finalizado':
        #    self.fields['usuario'] = forms.ModelChoiceField(Proyecto.objects.get(pk=kwargs['instance'].pk).equipo.all(),
        #                                                    required=False,
        #                                                    widget=forms.HiddenInput(attrs={'value':user_story.usuario}))


        #self.fields['usuario'].initial = user
        self.fields['id'].initial = user_story.id
        self.fields['prioridad'].intial = user_story.prioridad
        self.fields['valor_tecnico'].initial = user_story.valor_tecnico
        self.fields['estimacion'].initial = user_story.estimacion
        print "prioridad initial = %s" % self.fields['prioridad'].initial
        print "valor_tecnico initial = %s" % self.fields['valor_tecnico'].initial
        #self.fields['usuario'].initial = user_story.usuario
        #self.fields['estado'].initial = user_story.estado
        #self.fields['flujo'].initial = user_story.flujo
        #self.fields['sprint'].initial = user_story.sprint

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        cleaned_data = super(UserStoryUpdateFormSM, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        proyecto = super(UserStoryUpdateFormSM, self).save(commit=True)
        #user_story = UserStory.objects.get(pk=self.context[''])
        user_story = UserStory.objects.get(pk=self.cleaned_data['id'])
        #user_story.prioridad = self.cleaned_data['prioridad']
        #user_story.valor_tecnico = self.cleaned_data['valor_tecnico']
        #user_story.estimacion = self.cleaned_data['estimacion']
        #user_story.usuario = self.cleaned_data['usuario']

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


        #user_story.estado = self.cleaned_data['estado']

        #user_story.flujo = self.cleaned_data['flujo']
        #user_story.sprint = self.cleaned_data['sprint']
        user_story.save()

        #historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', usuario=self.user)
        #historial_us.save()

        return proyecto