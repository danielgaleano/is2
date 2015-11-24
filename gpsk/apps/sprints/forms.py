from django import forms
from django.core.exceptions import ObjectDoesNotExist
from db_file_storage.form_widgets import DBClearableFileInput

from models import Sprint
from apps.proyectos.models import Proyecto
from apps.proyectos.views import habiles
from apps.user_stories.models import UserStory, HistorialUserStory, UserStoryDetalle, Tarea, Nota, Adjunto
from apps.flujos.models import Flujo




# 1 MB - 1048576
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
MAX_UPLOAD_SIZE = "1048576"


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

    def clean_duracion(self):
        duracion = self.cleaned_data['duracion']
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        duracion_proyecto = habiles(proyecto.fecha_inicio, proyecto.fecha_fin)
        lista_sprints = Sprint.objects.filter(proyecto=proyecto).order_by('pk')

        duracion_total_sprints = 0
        for sprint in lista_sprints:
            duracion_total_sprints = duracion_total_sprints + sprint.duracion

        print "duracion_total_sprints %s" % duracion_total_sprints

        total = duracion_total_sprints + duracion

        if total > duracion_proyecto:
            print("duracion mayor")
            raise forms.ValidationError("La duracion de los sprints no debe ser mayor a la del proyecto.\n"
                                        "Sugerencia: Aumente la duracion del proyecto.")

        if duracion == 0:
            raise forms.ValidationError("La duracion del sprint debe ser mayor a cero.")

        return duracion

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

    def clean_duracion(self):
        duracion = self.cleaned_data['duracion']
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        duracion_proyecto = habiles(proyecto.fecha_inicio, proyecto.fecha_fin)
        lista_sprints = Sprint.objects.filter(proyecto=proyecto).order_by('pk')

        duracion_total_sprints = 0
        for sprint in lista_sprints:
            duracion_total_sprints = duracion_total_sprints + sprint.duracion

        print "duracion_total_sprints %s" % duracion_total_sprints

        total = duracion_total_sprints + duracion

        if total > duracion_proyecto:
            print("duracion mayor")
            raise forms.ValidationError("La duracion de los sprints no debe ser mayor a la del proyecto.\n"
                                        "Sugerencia: Aumente la duracion del proyecto.")

        if duracion == 0:
            raise forms.ValidationError("La duracion del sprint debe ser mayor a cero.")

        return duracion

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
        user_story_string = kwargs['initial']['user_story']
        rol_developer = kwargs['initial']['users_rol_developer']
        kwargs.pop('initial')

        user_story = UserStory.objects.get(pk=user_story_string.pk)
        sprint = Sprint.objects.get(pk=sprint_string.pk)
        proyecto = Proyecto.objects.get(pk=proyecto_string.pk)

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

        # self.fields['user_story'] = forms.ModelChoiceField(UserStory.objects.filter(proyecto=proyecto).exclude(Q(estado='Activo') |
        #                                                                                                       Q(estado='Descartado') |
        #                                                                                                       Q(estado='Finalizado') |
        #                                                                                                       Q(estado='Aprobado') |
        #                                                                                                       Q(sprint=sprint)).order_by('-prioridad'))
        print "modelfield = %s" % UserStory.objects.all()
        print " user_story = %s" % user_story.pk

        self.fields['user_story'] = forms.ModelChoiceField(UserStory.objects.all(), required=False, widget=forms.HiddenInput())

        self.fields['desarrollador'] = forms.ModelChoiceField(
            Proyecto.objects.get(pk=proyecto.pk).equipo.all().filter(pk__in=pk_rol),
            required=True)
        self.fields['estado'] = forms.ChoiceField(choices=ESTADO_USER_STORY, widget=forms.HiddenInput(), required=False)

        #flitrar solo los flujos del proyecto
        self.fields['flujo'] = forms.ModelChoiceField(Flujo.objects.filter(proyecto=proyecto).order_by('pk'), required=True)
        #flitrar solo los sprints del proyecto
        self.fields['sprint'] = forms.ModelChoiceField(Sprint.objects.filter(proyecto=proyecto).order_by('pk'),
                                                       required=False, widget=forms.HiddenInput())

        self.fields['proyecto'] = forms.ModelChoiceField(Proyecto.objects.all(), widget=forms.HiddenInput(), required=False)

        self.fields['user_story'].initial = user_story.id
        self.fields['proyecto'].initial = proyecto.id
        self.fields['sprint'].initial = sprint.id

    nombre = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Sprint
        fields = ['nombre']

    def save(self, commit=True):
        cleaned_data = super(SprintAsignarUserStoryForm, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        #proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = super(SprintAsignarUserStoryForm, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['user_story'].pk)

        old_flujo = user_story.flujo

        user_story.flujo = self.cleaned_data['flujo']
        user_story.estado = 'Activo'

        user_story.usuario = self.cleaned_data['desarrollador']
        user_story.sprint = sprint

        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="desarrollador",
                                              valor=self.cleaned_data['desarrollador'], usuario=self.user)
        historial_us.save()

        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="flujo",
                                              valor=self.cleaned_data['flujo'], usuario=self.user)
        historial_us.save()

        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="sprint",
                                              valor=sprint, usuario=self.user)
        historial_us.save()


        historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="estado",
                                              valor='Activo', usuario=self.user)
        historial_us.save()

        user_story.save()


        actividades = user_story.flujo.actividades.all()
        print "Actividades asignar %s" % actividades
        for a in actividades:
            print "act: %s - %s" % (a.pk, a)
        estados = actividades[0].estados.all()
        existe = True
        try:
            detalle = UserStoryDetalle.objects.get(user_story=user_story)
            if detalle.user_story.flujo == user_story.flujo:
                pass
            # si se cambia de flujo a un user_story pendiente
            else:

                detalle.actividad = actividades[0]
                detalle.estado = estados[0]
                detalle.save()
        except ObjectDoesNotExist:
            print 'No existe el user story!'
            existe = False
        if existe:
            pass
        else:
            print "act_else: %s - %s" % (actividades[0].pk, actividades[0])
            detalle = UserStoryDetalle(user_story=user_story, actividad=actividades[0], estado=estados[0])
            detalle.save()

        return sprint

'''
    def clean_user_story(self):
        sprint = super(SprintAsignarUserStoryForm, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['user_story'].pk)

        proyecto = Proyecto.objects.get(pk=self.data.get('proyecto'))

        user_story_list_sprint = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')
        rol_developer = RolProyecto.objects.get(group__name='Developer')
        miembros = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer)
        cantidad_developers = miembros.count()

        developer = RolProyecto_Proyecto.objects.filter(user=self.data.get('desarrollador'), proyecto=proyecto,
                                                        rol_proyecto=rol_developer)

        horas_asignadas_sprint = 0
        for us in user_story_list_sprint:
            horas_asignadas_sprint = horas_asignadas_sprint + us.estimacion

        horas_totales_sprint = 0
        for miembro in miembros:
            horas_developer_sprint = 0
            horas_developer_sprint = miembro.horas_developer * sprint.duracion
            horas_totales_sprint = horas_totales_sprint + horas_developer_sprint

        #horas_totales_sprint = sprint.duracion * cantidad_developers * 8
        horas_disponibles = horas_totales_sprint - horas_asignadas_sprint

        horas_disponibles = horas_disponibles - user_story.estimacion


        user_story_list_sprint_usuario = UserStory.objects.filter(usuario=developer[0].user, sprint=sprint)
        total_horas_us_user = 0
        for us in user_story_list_sprint_usuario:
            total_horas_us_user = total_horas_us_user + us.estimacion

        horas_developer_sprint = developer[0].horas_developer * sprint.duracion
        horas_disponibles_developer = horas_developer_sprint - total_horas_us_user
        horas_disponibles_developer = horas_disponibles_developer - user_story.estimacion

        if horas_disponibles_developer < 0:
            raise forms.ValidationError("El desarrollador no tiene las horas disponibles solicitadas.")

        if horas_disponibles < 0:
            raise forms.ValidationError("No existen suficientes horas disponibles para asignar en el sprint.")

        return horas_disponibles
'''


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
        proyecto = Proyecto.objects.get(pk=proyecto_string.pk)

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
        self.fields['flujo'] = forms.ModelChoiceField(Flujo.objects.filter(proyecto=proyecto).order_by('pk'), required=True)
        #flitrar solo los sprints del proyecto
        self.fields['sprint'] = forms.ModelChoiceField(Sprint.objects.filter(proyecto=proyecto).order_by('pk'),
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
        #proyecto = Proyecto.objects.get(pk=self.instance.pk)

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


class RegistrarTareaForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(RegistrarTareaForm, self).__init__(*args, **kwargs)
        self.user = user

        user_story_string = kwargs['initial']['user_story']
        sprint_string = kwargs['initial']['sprint']
        proyecto_string = kwargs['initial']['proyecto']
        rol_developer = kwargs['initial']['users_rol_developer']
        kwargs.pop('initial')

        user_story = UserStory.objects.get(pk=user_story_string.pk)
        sprint = Sprint.objects.get(pk=sprint_string.pk)
        proyecto = Proyecto.objects.get(pk=proyecto_string.pk)

        pk_rol = []
        for rol in rol_developer:
            pk_rol.append(rol.pk)

        self.fields['id'] = forms.ModelChoiceField(UserStory.objects.filter(proyecto=proyecto).order_by('-prioridad'),
                                                   widget=forms.HiddenInput())

        self.fields['descripcion'] = forms.CharField(max_length=140, required=True, widget=forms.Textarea(attrs={'required': True}))
        self.fields['horas'] = forms.IntegerField(required=True, min_value=0)

        self.fields['id'].initial = user_story.id

    nombre = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Sprint
        fields = ['nombre']

    def save(self, commit=True):
        cleaned_data = super(RegistrarTareaForm, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        #proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = super(RegistrarTareaForm, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['id'].pk)

        tarea = Tarea()
        tarea.user_story = user_story
        tarea.descripcion = self.cleaned_data['descripcion']
        tarea.horas_de_trabajo = self.cleaned_data['horas']
        tarea.sprint = sprint
        tarea.flujo = user_story.flujo
        tarea.actividad = user_story.userstorydetalle.actividad
        tarea.estado = user_story.userstorydetalle.estado
        tarea.tipo = 'Registro de Tarea'
        tarea.usuario = self.user
        tarea.save()

        user_story.horas_acumuladas = user_story.horas_acumuladas + tarea.horas_de_trabajo
        user_story.save()

        return sprint


class AdjuntarArchivoForm(forms.Form):
    archivo = forms.FileField()

    #def clean_archivo(self):
    #    print "clean"
    #    archivo = self.cleaned_data['archivo']
    #    if archivo._size > MAX_UPLOAD_SIZE:
    #        print "if"
    #        raise forms.ValidationError('Archivo mayor a %s. Su archivo tiene %s' % (defaultfilters.filesizeformat(MAX_UPLOAD_SIZE), defaultfilters.filesizeformat(archivo._size)))

    #    return archivo


class AgregarAdjuntoForm(forms.ModelForm):
    class Meta:
        model = Adjunto
        exclude = ['user_story']
        widgets = {
            'archivo': DBClearableFileInput
        }

    #def clean_archivo(self):
        #print "clean"
        #archivo = self.cleaned_data['archivo']
        #print archivo
        #print self.cleaned_data['archivo']
        #if archivo._size > MAX_UPLOAD_SIZE:
        #    print "if"
        #    raise forms.ValidationError('Archivo mayor a %s. Su archivo tiene %s' % (defaultfilters.filesizeformat(MAX_UPLOAD_SIZE), defaultfilters.filesizeformat(archivo._size)))


class AgregarNotaForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(AgregarNotaForm, self).__init__(*args, **kwargs)
        self.user = user

        user_story_string = kwargs['initial']['user_story']
        sprint_string = kwargs['initial']['sprint']
        proyecto_string = kwargs['initial']['proyecto']
        rol_developer = kwargs['initial']['users_rol_developer']
        kwargs.pop('initial')

        user_story = UserStory.objects.get(pk=user_story_string.pk)
        sprint = Sprint.objects.get(pk=sprint_string.pk)
        proyecto = Sprint.objects.get(pk=proyecto_string.pk)

        #pk_rol = []
        #for rol in rol_developer:
        #    pk_rol.append(rol.pk)

        print "init nota = %s" % user_story

        self.fields['id'] = forms.ModelChoiceField(UserStory.objects.all(), widget=forms.HiddenInput())

        self.fields['texto'] = forms.CharField(max_length=140, required=True, widget=forms.Textarea(attrs={'required': True}))
        #self.fields['proyecto'] = forms.ModelChoiceField(Proyecto.objects.all(), widget=forms.HiddenInput())

        self.fields['id'].initial = user_story.id
        #self.fields['proyecto'].initial = proyecto.id


    texto = forms.CharField(max_length=140, required=True, widget=forms.Textarea(attrs={'required': True}))
    nombre = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Sprint
        fields = ['nombre']

    def save(self, commit=True):
        print "saaaaa"
        cleaned_data = super(AgregarNotaForm, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        #proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = super(AgregarNotaForm, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['id'].pk)
        #proyecto = Proyecto.objects.get(pk=self.cleaned_data['proyecto'].pk)

        nota = Nota()
        nota.texto = self.cleaned_data['texto']
        nota.user_story = user_story
        nota.usuario = self.user

        print "save nota = %s" % user_story

        user_story.estado = 'Aprobado'
        user_story.save()

        tarea = Tarea()
        tarea.user_story = user_story
        tarea.descripcion = "Aprobar user story"
        tarea.horas_de_trabajo = 0
        tarea.sprint = sprint
        tarea.flujo = user_story.flujo
        tarea.actividad = user_story.userstorydetalle.actividad
        tarea.estado = user_story.userstorydetalle.estado
        tarea.tipo = 'Cambio de Estado'
        tarea.usuario = self.user
        tarea.save()

        historial_us = HistorialUserStory(user_story=user_story, operacion='aprobado', usuario=self.user)
        historial_us.save()






        nota.save()

        return sprint


class AgregarNotaFormNoAprobar(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(AgregarNotaFormNoAprobar, self).__init__(*args, **kwargs)
        self.user = user

        user_story_string = kwargs['initial']['user_story']
        sprint_string = kwargs['initial']['sprint']
        proyecto_string = kwargs['initial']['proyecto']
        rol_developer = kwargs['initial']['users_rol_developer']
        kwargs.pop('initial')

        user_story = UserStory.objects.get(pk=user_story_string.pk)
        sprint = Sprint.objects.get(pk=sprint_string.pk)
        proyecto = Proyecto.objects.get(pk=proyecto_string.pk)

        #pk_rol = []
        #for rol in rol_developer:
        #    pk_rol.append(rol.pk)

        print "init nota = %s" % user_story

        self.fields['id'] = forms.ModelChoiceField(UserStory.objects.all(), widget=forms.HiddenInput())

        self.fields['texto'] = forms.CharField(max_length=140, required=True, widget=forms.Textarea(attrs={'required': True, 'class': 'form-control', 'rows': '3'}))
        #self.fields['proyecto'] = forms.ModelChoiceField(Proyecto.objects.all(), widget=forms.HiddenInput())

        self.fields['id'].initial = user_story.id
        #self.fields['proyecto'].initial = proyecto.id


    texto = forms.CharField(max_length=140, required=True, widget=forms.Textarea(attrs={'required': True}))
    nombre = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Sprint
        fields = ['nombre']

    def save(self, commit=True):
        print "saaaaa"
        cleaned_data = super(AgregarNotaFormNoAprobar, self).clean()
        #usuario = Usuario.objects.get(user=self.instance)
        #proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = super(AgregarNotaFormNoAprobar, self).save(commit=True)

        user_story = UserStory.objects.get(pk=self.cleaned_data['id'].pk)
        #proyecto = Proyecto.objects.get(pk=self.cleaned_data['proyecto'].pk)

        nota = Nota()
        nota.texto = self.cleaned_data['texto']
        nota.user_story = user_story
        nota.usuario = self.user

        print "save nota = %s" % user_story

        user_story.save()

        nota.save()

        return sprint