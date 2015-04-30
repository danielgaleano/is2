from django import forms
from django.db.models import Q

from models import Sprint
from apps.proyectos.models import Proyecto
from apps.flujos.models import Flujo
from apps.user_stories.models import UserStory, HistorialUserStory


class SprintCreateForm(forms.ModelForm):
    def __init__(self, user, **kwargs):
        super(SprintCreateForm, self).__init__(**kwargs)
        self.user = user
    #modificar para que filtre solo los flujos del proyecto
    #flujos = forms.ModelMultipleChoiceField(Flujo.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    duracion = forms.IntegerField(min_value=0, max_value=30, help_text='En dias. Maximo 30 dias.')

    class Meta:
        model = Sprint
        fields = ['nombre', 'duracion']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create Sprint without database save")
        #userStory = super(UserStoryCreateForm, self).save(commit=True)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = Sprint.objects.create(nombre=self.cleaned_data['nombre'],
                                       duracion=self.cleaned_data['duracion'],
                                       proyecto=proyecto)

        #for flujo in self.cleaned_data['flujos']:
        #    sprint.flujos.add(flujo)

        sprint.save()

        return proyecto


class SprintUpdateForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(SprintUpdateForm, self).__init__(*args, **kwargs)
        self.user = user

        #flujos = kwargs['initial']['flujos']
        sprint_string = kwargs['initial']['sprint']
        kwargs.pop('initial')

        #self.fields['rolproyecto'] = forms.ModelMultipleChoiceField(Group.objects.all().filter(rolproyecto__es_rol_proyecto=True).exclude(name='Scrum Master'),
        #        widget=forms.CheckboxSelectMultiple, required=False)

        #dic = {}
        #for arr in roles:
        #    dic[arr.pk] = arr
        #self.fields['rolproyecto'].initial = dic

        sprint = Sprint.objects.get(pk=sprint_string.pk)

        #self.fields['usuario'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['nombre'] = forms.CharField(required=True)
        self.fields['duracion'] = forms.IntegerField(min_value=0, max_value=30, help_text='En dias. Maximo 30 dias.')
        #modificar para filtrar solo flujos del proyecto
        #self.fields['flujos'] = forms.ModelMultipleChoiceField(Flujo.objects.all(),
        #                                                       widget=forms.CheckboxSelectMultiple, required=False)

        #dic = {}
        #for arr in flujos:
        #    dic[arr.pk] = arr
        #self.fields['rolproyecto'].initial = dic

        #self.fields['usuario'].initial = user
        self.fields['id'].initial = sprint.id
        self.fields['nombre'].initial = sprint.nombre
        self.fields['duracion'].initial = sprint.duracion
        #self.fields['flujos'].initial = dic

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        #usuario = Usuario.objects.get(user=self.instance)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        proyecto = super(SprintUpdateForm, self).save(commit=True)
        #user_story = UserStory.objects.get(pk=self.context[''])
        sprint = Sprint.objects.get(pk=self.cleaned_data['id'])
        sprint.nombre = self.cleaned_data['nombre']
        sprint.duracion = self.cleaned_data['duracion']

        #for flujo in self.cleaned_data['flujos']:
        #    sprint.flujos.add(flujo)

        #lista_flujos_en_sp = sprint.flujos.all()
        #for item1 in lista_flujos_en_sp:
        #    if item1 not in self.cleaned_data['flujos']:
        #        flujo1 = Flujo.objects.get(pk=item1.pk)
        #        #RolProyecto_Proyecto.objects.get(user=user, rol_proyecto=flujo1, proyecto=proyecto).delete()
        #        #grupo = Group.objects.get(name=flujo1.group.name)
        #        sprint.flujos.remove(flujo1)

        sprint.save()

        return proyecto


class SprintAsignarUserStoryForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(SprintAsignarUserStoryForm, self).__init__(*args, **kwargs)
        self.user = user

        sprint_string = kwargs['initial']['sprint']
        proyecto_string = kwargs['initial']['proyecto']
        rol_developer = kwargs['initial']['users_rol_developer']
        kwargs.pop('initial')

        sprint = Sprint.objects.get(pk=sprint_string.pk)
        proyecto = Sprint.objects.get(pk=proyecto_string.pk)

        ESTADO_USER_STORY=(
        ('No asignado', 'No asignado'),
        ('Activo', 'Activo'),
        ('Pendiente', 'Pendiente'),
        ('Finalizado', 'Finalizado'),
        ('Aprobado', 'Aprobado'),
        ('Descartado', 'Descartado'),
        )

        pk_rol = []
        for rol in rol_developer:
            pk_rol.append(rol.pk)

        self.fields['user_story'] = forms.ModelChoiceField(UserStory.objects.filter(proyecto=proyecto).exclude(Q(estado='Activo') |
                                                                                                               Q(estado='Descartado') |
                                                                                                               Q(estado='Finalizado') |
                                                                                                               Q(estado='Aprobado') |
                                                                                                               Q(sprint=sprint)).order_by('-prioridad'))
        print "modelfield = %s" % UserStory.objects.all()
        self.fields['desarrollador'] = forms.ModelChoiceField(
            Proyecto.objects.get(pk=proyecto.pk).equipo.all().filter(pk__in=pk_rol),
            required=True)
        self.fields['estado'] = forms.ChoiceField(choices=ESTADO_USER_STORY, widget=forms.HiddenInput(), required=False)
        #flitrar solo los flujos del proyecto
        self.fields['flujo'] = forms.ModelChoiceField(Flujo.objects.all(), required=True)
        #flitrar solo los sprints del proyecto
        self.fields['sprint'] = forms.ModelChoiceField(Sprint.objects.filter(proyecto=kwargs['instance'].pk).order_by('pk'),
                                                       required=False, widget=forms.HiddenInput())

        self.fields['sprint'].initial = sprint.id

    nombre = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Sprint
        fields = ['nombre']

    def save(self, commit=True):
        cleaned_data = super(SprintAsignarUserStoryForm, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = super(SprintAsignarUserStoryForm, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['user_story'].pk)



        user_story.usuario = self.cleaned_data['desarrollador']
        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="desarrollador",
                                              valor=self.cleaned_data['desarrollador'], usuario=self.user)
        historial_us.save()
        user_story.flujo = self.cleaned_data['flujo']
        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="flujo",
                                              valor=self.cleaned_data['flujo'], usuario=self.user)
        historial_us.save()
        user_story.sprint = sprint
        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="sprint",
                                              valor=sprint, usuario=self.user)
        historial_us.save()
        user_story.estado = 'Activo'

        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="estado",
                                              valor='Activo', usuario=self.user)
        historial_us.save()

        user_story.save()

        return sprint


class SprintUpdateUserStoryForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(SprintUpdateUserStoryForm, self).__init__(*args, **kwargs)
        self.user = user

        user_story_string = kwargs['initial']['user_story']
        sprint_string = kwargs['initial']['sprint']
        proyecto_string = kwargs['initial']['proyecto']
        rol_developer = kwargs['initial']['users_rol_developer']
        kwargs.pop('initial')

        user_story = UserStory.objects.get(pk=user_story_string.pk)
        sprint = Sprint.objects.get(pk=sprint_string.pk)
        proyecto = Sprint.objects.get(pk=proyecto_string.pk)

        ESTADO_USER_STORY=(
        ('No asignado', 'No asignado'),
        ('Activo', 'Activo'),
        ('Pendiente', 'Pendiente'),
        ('Finalizado', 'Finalizado'),
        ('Aprobado', 'Aprobado'),
        ('Descartado', 'Descartado'),
        )

        pk_rol = []
        for rol in rol_developer:
            pk_rol.append(rol.pk)

        self.fields['id'] = forms.CharField(required=True, widget=forms.HiddenInput())

        self.fields['desarrollador'] = forms.ModelChoiceField(
            Proyecto.objects.get(pk=proyecto.pk).equipo.all().filter(pk__in=pk_rol),
            required=True)

        self.fields['estado'] = forms.ChoiceField(choices=ESTADO_USER_STORY, widget=forms.HiddenInput(), required=False)
        #flitrar solo los flujos del proyecto
        self.fields['flujo'] = forms.ModelChoiceField(Flujo.objects.all(), required=True)
        #flitrar solo los sprints del proyecto
        self.fields['sprint'] = forms.ModelChoiceField(Sprint.objects.filter(proyecto=kwargs['instance'].pk).order_by('pk'),
                                                       required=False, widget=forms.HiddenInput())

        self.fields['id'].initial = user_story.id
        self.fields['desarrollador'].initial = user_story.usuario
        self.fields['estado'].initial = user_story.estado
        self.fields['flujo'].initial = user_story.flujo
        self.fields['sprint'].initial = user_story.sprint

    nombre = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Sprint
        fields = ['nombre']

    def save(self, commit=True):
        cleaned_data = super(SprintUpdateUserStoryForm, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = super(SprintUpdateUserStoryForm, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['id'])

        if user_story.usuario != cleaned_data['desarrollador']:
            user_story.usuario = self.cleaned_data['desarrollador']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="desarrollador",
                                              valor=self.cleaned_data['desarrollador'], usuario=self.user)
            historial_us.save()

        if user_story.flujo != self.cleaned_data['flujo']:
            user_story.flujo = self.cleaned_data['flujo']
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="flujo",
                                                  valor=self.cleaned_data['flujo'], usuario=self.user)
            historial_us.save()

        user_story.sprint = self.cleaned_data['sprint']

        user_story.estado = self.cleaned_data['estado']
        user_story.save()

        return sprint