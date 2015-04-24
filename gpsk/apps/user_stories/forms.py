from django import forms
from models import UserStory, HistorialUserStory
from apps.proyectos.models import Proyecto
from apps.flujos.models import Flujo
from apps.sprints.models import Sprint


class UserStoryCreateForm(forms.ModelForm):
    def __init__(self, user, **kwargs):
        super(UserStoryCreateForm, self).__init__(**kwargs)
        self.user = user

    class Meta:
        model = UserStory
        fields = ['nombre', 'descripcion', 'valor_negocio', 'prioridad']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create UserStory without database save")
        #userStory = super(UserStoryCreateForm, self).save(commit=True)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        userStory = UserStory.objects.create(nombre=self.cleaned_data['nombre'],
                                             descripcion=self.cleaned_data['descripcion'],
                                             valor_negocio=self.cleaned_data['valor_negocio'],
                                             prioridad=self.cleaned_data['prioridad'],
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

        PRIORIDAD_USER_STORY=(
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
    )

        #self.fields['usuario'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['nombre'] = forms.CharField(required=True)
        self.fields['descripcion'] = forms.CharField(required=True)
        self.fields['valor_negocio'] = forms.IntegerField(required=True, min_value=0, max_value=100)
        self.fields['prioridad'] = forms.ChoiceField(choices=PRIORIDAD_USER_STORY)

        #self.fields['usuario'].initial = user
        self.fields['id'].initial = user_story.id
        self.fields['nombre'].initial = user_story.nombre
        self.fields['descripcion'].initial = user_story.descripcion
        self.fields['valor_negocio'].initial = user_story.valor_negocio
        self.fields['prioridad'].initial = user_story.prioridad

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        #usuario = Usuario.objects.get(user=self.instance)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        proyecto = super(UserStoryUpdateFormPO, self).save(commit=True)
        #user_story = UserStory.objects.get(pk=self.context[''])
        user_story = UserStory.objects.get(pk=self.cleaned_data['id'])
        user_story.nombre = self.cleaned_data['nombre']
        user_story.descripcion = self.cleaned_data['descripcion']
        user_story.valor_negocio = self.cleaned_data['valor_negocio']
        user_story.prioridad = self.cleaned_data['prioridad']
        user_story.save()

        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', usuario=self.user)
        historial_us.save()

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

        PRIORIDAD_USER_STORY=(
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
        )
        ESTADO_USER_STORY=(
        ('No asignado', 'No asignado'),
        ('Activo', 'Activo'),
        ('Finalizado', 'Finalizado'),
        ('Aprobado', 'Aprobado'),
        ('Descartado', 'Descartado'),
        )
        #self.fields['usuario'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['valor_tecnico'] = forms.IntegerField(required=True, min_value=0, max_value=100)
        self.fields['estimacion'] = forms.IntegerField(required=True, min_value=0, max_value=176,
                                                       help_text='En horas. Maximo 176 horas.')
        self.fields['usuario'] = forms.ModelChoiceField(Proyecto.objects.get(pk=kwargs['instance'].pk).equipo.all(),
                                                        required=False)
        self.fields['estado'] = forms.ChoiceField(choices=ESTADO_USER_STORY, widget=forms.HiddenInput())
        #flitrar solo los flujos del proyecto
        self.fields['flujo'] = forms.ModelChoiceField(Flujo.objects.all(), required=False)
        #flitrar solo los sprints del proyecto
        self.fields['sprint'] = forms.ModelChoiceField(Sprint.objects.filter(proyecto=kwargs['instance'].pk).order_by('pk'),
                                                       required=False)

        if str(user_story.estado) == 'Finalizado':
            self.fields['usuario'] = forms.ModelChoiceField(Proyecto.objects.get(pk=kwargs['instance'].pk).equipo.all(),
                                                            required=False,
                                                            widget=forms.HiddenInput(attrs={'value':user_story.usuario}))


        #self.fields['usuario'].initial = user
        self.fields['id'].initial = user_story.id
        self.fields['valor_tecnico'].initial = user_story.valor_tecnico
        self.fields['estimacion'].initial = user_story.estimacion
        self.fields['usuario'].initial = user_story.usuario
        self.fields['estado'].initial = user_story.estado
        self.fields['flujo'].initial = user_story.flujo
        self.fields['sprint'].initial = user_story.sprint

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        #usuario = Usuario.objects.get(user=self.instance)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        proyecto = super(UserStoryUpdateFormSM, self).save(commit=True)
        #user_story = UserStory.objects.get(pk=self.context[''])
        user_story = UserStory.objects.get(pk=self.cleaned_data['id'])
        user_story.valor_tecnico = self.cleaned_data['valor_tecnico']
        user_story.estimacion = self.cleaned_data['estimacion']
        user_story.usuario = self.cleaned_data['usuario']

        if user_story.usuario is None:
            user_story.estado = 'No asignado'
        elif user_story.usuario is not None:
            if str(user_story.estado) == 'Finalizado' or str(user_story.estado) == 'Aprobado':
                pass
            else:
                user_story.estado = 'Activo'

        #user_story.estado = self.cleaned_data['estado']

        user_story.flujo = self.cleaned_data['flujo']
        user_story.sprint = self.cleaned_data['sprint']
        user_story.save()

        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', usuario=self.user)
        historial_us.save()

        return proyecto