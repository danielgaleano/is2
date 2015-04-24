import itertools

from django import forms
from django.utils.text import slugify
from models import Proyecto
from django.contrib.auth.models import User, Group
from apps.roles_proyecto.models import RolProyecto, RolProyecto_Proyecto
from apps.usuarios.models import Usuario
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class ProyectoCreateForm(forms.ModelForm):
    scrum_master = forms.ModelChoiceField(User.objects.exclude(is_staff=True))
    # fecha_inicio = forms.DateField()
    # fecha_fin = forms.DateField()
    # fecha_inicio = forms.CharField()
    # codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['cliente', 'nombre_corto', 'nombre_largo', 'scrum_master', 'fecha_inicio', 'fecha_fin']

    def clean_fecha_fin(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']
        fecha_fin = self.cleaned_data['fecha_fin']

        if fecha_fin <= fecha_inicio:
            raise forms.ValidationError("La fecha de finalizacion del proyecto debe ser posterior a la de fecha de inicio.")

        return fecha_fin

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create Proyecto without database save")
        proyecto = super(ProyectoCreateForm, self).save(commit=True)
        scrum_master = User.objects.get(pk=self.cleaned_data['scrum_master'].pk)

        rolproyecto = RolProyecto.objects.get(group__name='Scrum Master')
        grupo = Group.objects.get(name='Scrum Master')
        #Se agrega al usuario al equipo
        proyecto.equipo.add(scrum_master)
        #Se agrega el rol al usuario
        scrum_master.usuario.rolesproyecto.add(rolproyecto)
        scrum_master.groups.add(grupo)
        #Se agrega el registro de la asignacion del rol a la tabla USER_ROLPROYECTO_PROYECTO
        rolproyecto_proyecto = RolProyecto_Proyecto(user=scrum_master, rol_proyecto=rolproyecto, proyecto=proyecto)
        

        max_length = Proyecto._meta.get_field('codigo').max_length
        proyecto.codigo = orig = slugify(proyecto.nombre_corto[0])[:max_length]

        for x in itertools.count(1):
            if not Proyecto.objects.filter(codigo=proyecto.codigo).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            proyecto.codigo = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        proyecto.save()



        rolproyecto_proyecto.save()

        scrum_master.save()


        return proyecto


class ProyectoUpdateForm(forms.ModelForm):
    scrum_master = forms.ModelChoiceField(User.objects.exclude(is_staff=True))

    class Meta:
        model = Proyecto
        fields = ['cliente', 'nombre_corto', 'nombre_largo', 'scrum_master', 'fecha_inicio', 'fecha_fin', 'estado']

    def clean_fecha_fin(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']
        fecha_fin = self.cleaned_data['fecha_fin']

        if fecha_fin <= fecha_inicio:
            raise forms.ValidationError("La fecha de finalizacion del proyecto debe ser posterior a la de fecha de inicio.")

        return fecha_fin

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create Proyecto without database save")
        proyecto = super(ProyectoUpdateForm, self).save(commit=True)
        proyecto_antiguo = Proyecto.objects.get(pk=self.instance.pk)
        print proyecto
        print proyecto_antiguo
        estado = self.cleaned_data['estado']

        scrum_master = User.objects.get(pk=self.cleaned_data['scrum_master'].pk)

        rolproyecto = RolProyecto.objects.get(group__name='Scrum Master')
        grupo = Group.objects.get(name='Scrum Master')

        #obtenemos esl usuario anterior con el rol scrum master
        usuario_anterior = proyecto_antiguo.scrum_master
        #asignamos al nuevo usuario como scrum master del proyecto
        proyecto.scrum_master = scrum_master
        #asignamos el nuevo estado
        proyecto.estado = estado
        #obtenemos el registro anterior

        print "lisssss %s %s %s" % (usuario_anterior, rolproyecto, proyecto_antiguo)

        print "anterior %s actual %s" % (usuario_anterior, scrum_master)

        for miembro in proyecto_antiguo.equipo.all():
            if miembro != scrum_master:
                try:
                    entrar = RolProyecto_Proyecto.objects.get(user=miembro, rol_proyecto=rolproyecto, proyecto=proyecto_antiguo)
                except ObjectDoesNotExist:
                    entrar = None
                print entrar
                if entrar:
                    print "entro"
                    row = RolProyecto_Proyecto.objects.get(user=miembro, rol_proyecto=rolproyecto, proyecto=proyecto_antiguo)
                    print "for"
                    print row
                    if row:
                        row.delete()

                    else:
                        pass



        #se le quita el rol Scrum master al usuario_anterior
        usuario_anterior.groups.remove(grupo)
        #Se agrega como rol de proyecto y como group        
        scrum_master.usuario.rolesproyecto.add(rolproyecto)
        scrum_master.groups.add(grupo)


        #Se agrega al usuario al equipo
        proyecto.equipo.add(scrum_master)
        #Se agrega el rol al usuario
        scrum_master.usuario.rolesproyecto.add(rolproyecto)
        #Se agrega el registro de la asignacion del rol a la tabla USER_ROLPROYECTO_PROYECTO
        rolproyecto_proyecto = RolProyecto_Proyecto(user=scrum_master, rol_proyecto=rolproyecto, proyecto=proyecto)
        

        rolproyecto_proyecto.save()

        proyecto.save()
        scrum_master.save()


        return proyecto

    


class AddMiembroForm(forms.ModelForm):
    # nombre = forms.CharField()
    def __init__(self, *args, **kwargs):
        context = super(AddMiembroForm, self).__init__(*args, **kwargs)
        miembros_actuales = Proyecto.objects.get(pk=kwargs['instance'].pk).equipo.all()
        print miembros_actuales
        # lista = User.objects.exclude(Q(is_staff=True) | Q(id__in=miembros_actuales))
        # print lista
        # for usuario in User.objects.all():
        #   for miembro in miembros_actuales:
        #       if usuario != 
        # lista_sin_actuales = Proyecto.objects.exclude(equipo=miembros_actuales)
        self.fields['usuario'] = forms.ModelChoiceField(User.objects.exclude(Q(is_staff=True) | Q(id__in=miembros_actuales)), required=True)
        print "hola"
        print self.fields['usuario']
        # self.fields['usuario'].initial = lista_sin_actuales

    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)
    # usuario = forms.ModelChoiceField(widget=forms.Select(None))
    # rolproyecto = forms.ModelChoiceField(RolProyecto.objects.all())
    rolproyecto = forms.ModelMultipleChoiceField(Group.objects.all().filter(rolproyecto__es_rol_proyecto=True).exclude(name='Scrum Master'), 
            widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        print "HeiHei"
        if not commit:
            print "errror"
            raise NotImplementedError("Can't create Miembro without database save")

        proyecto = super(AddMiembroForm, self).save(commit=True)

        user = User.objects.get(pk=self.cleaned_data['usuario'].pk)
        print user
        proyecto.equipo.add(user)
        usuario = Usuario.objects.get(user=user)
        # rol = Group.objects.get(pk=self.cleaned_data['rolproyecto'].pk)
        print self.cleaned_data['rolproyecto']
        for rol in self.cleaned_data['rolproyecto']:
            print rol
            grupo = Group.objects.get(name=rol.name)
            rolpro = RolProyecto.objects.get(group=rol)
            usuario.rolesproyecto.add(rolpro)
            user.groups.add(grupo)
            rolproyecto = RolProyecto.objects.get(group=rol)
            if RolProyecto_Proyecto.objects.filter(user=user, rol_proyecto=rolproyecto, proyecto=proyecto):
                nuevo = False
            else:
                if RolProyecto_Proyecto.objects.filter(rol_proyecto__group__name='Scrum Master', proyecto=proyecto) and rolproyecto.group.name == 'Scrum Master':
                    existe_sm = True
                    nuevo = False
                    print "%s en si" % rolproyecto
                else:
                    rolproyecto_proyecto = RolProyecto_Proyecto(user=user, rol_proyecto=rolproyecto, proyecto=proyecto)
                    rolproyecto_proyecto.save()
                    nuevo = True

        print nuevo
        if nuevo:
            usuario.save()
            proyecto.save()
            user.save()
        else:
            pass

        return proyecto


class RolMiembroForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        context = super(RolMiembroForm, self).__init__(*args, **kwargs)

        roles = kwargs['initial']['rolproyecto']
        user_string = kwargs['initial']['user']
        kwargs.pop('initial')
        
        self.fields['rolproyecto'] = forms.ModelMultipleChoiceField(Group.objects.all().filter(rolproyecto__es_rol_proyecto=True).exclude(name='Scrum Master'), 
                widget=forms.CheckboxSelectMultiple, required=False)

        dic = {}
        for arr in roles:
            dic[arr.pk] = arr
        self.fields['rolproyecto'].initial = dic

        user = User.objects.get(pk=user_string.pk)

        self.fields['usuario'] = forms.CharField(required=True, widget=forms.HiddenInput())


        self.fields['usuario'].initial = user

    # usuario = forms.CharField(widget=forms.HiddenInput(), required=True)
    codigo = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Proyecto
        fields = ['codigo']

    def save(self, commit=True):
        print "HeiHei"
        if not commit:
            print "errror"
            raise NotImplementedError("Can't create Miembro without database save")

        proyecto = super(RolMiembroForm, self).save(commit=True)

        user = User.objects.get(username=self.cleaned_data['usuario'])
        # user = User.objects.get(pk=self.cleaned_data['usuario'].pk)
        print user

        # proyecto.equipo.add(user)
        usuario = Usuario.objects.get(user=user)
        # rol = Group.objects.get(pk=self.cleaned_data['rolproyecto'].pk)
        nuevo = True
        print self.cleaned_data['rolproyecto']
        for rol in self.cleaned_data['rolproyecto']:
            print rol
            grupo = Group.objects.get(name=rol.name)
            rolpro = RolProyecto.objects.get(group=rol)
            usuario.rolesproyecto.add(rolpro)
            user.groups.add(grupo)
            rolproyecto = RolProyecto.objects.get(group=rol)
            #no importa
            if RolProyecto_Proyecto.objects.filter(user=user, rol_proyecto=rolproyecto, proyecto=proyecto):
                nuevo = False
            else:
                rolproyecto_proyecto = RolProyecto_Proyecto(user=user, rol_proyecto=rolproyecto, proyecto=proyecto)
                rolproyecto_proyecto.save()
                nuevo = True

        solo_del_usuario = RolProyecto_Proyecto.objects.filter(user=user, proyecto=proyecto)
        print "en form solo_del_usuario = %s" % solo_del_usuario
        #listar los roles en ese proyecto
        roles_proyecto_del_usuario = solo_del_usuario.values('rol_proyecto').distinct()
        print "en form roles_proyecto_del_usuario = %s" % roles_proyecto_del_usuario
        roro = Group.objects.filter(rolproyecto__pk__in=roles_proyecto_del_usuario)

        lista_de_roles_en_pro = roro

        print "lista_de_roles_en_pro = %s" % lista_de_roles_en_pro
        print "self.cleaned_data['rolproyecto'] = %s" % self.cleaned_data['rolproyecto']
        if lista_de_roles_en_pro == self.cleaned_data['rolproyecto']:
            print "Son listas iguales"
        else:
            print "Son listas diferentes"

            # for item2 in self.cleaned_data['rolproyecto']:
        for item1 in lista_de_roles_en_pro:
            if item1.name != 'Scrum Master':
                if item1 not in self.cleaned_data['rolproyecto']:
                    rol1 = RolProyecto.objects.get(group__pk=item1.pk)
                    RolProyecto_Proyecto.objects.get(user=user, rol_proyecto=rol1, proyecto=proyecto).delete()
                    grupo = Group.objects.get(name=rol1.group.name)
                    user.groups.remove(grupo)

        print nuevo
        if nuevo:
            usuario.save()
            # proyecto.save()
            user.save()
        else:
            pass

        return proyecto
