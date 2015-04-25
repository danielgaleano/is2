from django import forms

from models import Sprint
from apps.proyectos.models import Proyecto
from apps.flujos.models import Flujo


class SprintCreateForm(forms.ModelForm):
    def __init__(self, user, **kwargs):
        super(SprintCreateForm, self).__init__(**kwargs)
        self.user = user
    #modificar para que filtre solo los flujos del proyecto
    flujos = forms.ModelMultipleChoiceField(Flujo.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    duracion = forms.IntegerField(min_value=0, max_value=30, help_text='En dias. Maximo 30 dias.')

    class Meta:
        model = Sprint
        fields = ['nombre', 'duracion', 'flujos']

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create Sprint without database save")
        #userStory = super(UserStoryCreateForm, self).save(commit=True)
        proyecto = Proyecto.objects.get(pk=self.instance.pk)

        sprint = Sprint.objects.create(nombre=self.cleaned_data['nombre'],
                                       duracion=self.cleaned_data['duracion'],
                                       proyecto=proyecto)

        for flujo in self.cleaned_data['flujos']:
            sprint.flujos.add(flujo)

        sprint.save()

        return proyecto


class SprintUpdateForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        context = super(SprintUpdateForm, self).__init__(*args, **kwargs)
        self.user = user

        flujos = kwargs['initial']['flujos']
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
        self.fields['flujos'] = forms.ModelMultipleChoiceField(Flujo.objects.all(),
                                                               widget=forms.CheckboxSelectMultiple, required=False)

        dic = {}
        for arr in flujos:
            dic[arr.pk] = arr
        #self.fields['rolproyecto'].initial = dic

        #self.fields['usuario'].initial = user
        self.fields['id'].initial = sprint.id
        self.fields['nombre'].initial = sprint.nombre
        self.fields['duracion'].initial = sprint.duracion
        self.fields['flujos'].initial = dic

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

        for flujo in self.cleaned_data['flujos']:
            sprint.flujos.add(flujo)

        lista_flujos_en_sp = sprint.flujos.all()
        for item1 in lista_flujos_en_sp:
            if item1 not in self.cleaned_data['flujos']:
                flujo1 = Flujo.objects.get(pk=item1.pk)
                #RolProyecto_Proyecto.objects.get(user=user, rol_proyecto=flujo1, proyecto=proyecto).delete()
                #grupo = Group.objects.get(name=flujo1.group.name)
                sprint.flujos.remove(flujo1)

        sprint.save()

        return proyecto


