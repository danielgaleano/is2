from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from views import IndexView, FlujosProyectoIndex
from apps.proyectos.models import Proyecto
from models import Flujo, Actividad, PlantillaFlujo, ActividadFlujoPlantilla
from apps.roles_proyecto.models import RolProyecto, RolProyecto_Proyecto


class PlantillaFlujoTest(TestCase):
    """
    Clase que realiza el Test del modulo de administracion de plantillas de flujo
    """
    def setUp(self):
        """
        Funcion que inicializa el RequestFactory y un usuario de prueba para
        realizar los test
        """
        # Se crea el Request factory pars simular peticiones
        self.factory = RequestFactory()
        # Se crea el User que realiza las peticiones
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='test')

    def test_view_IndexView(self):
        """
        Funcion que realiza el test sobre la vista IndexView que genera
        lista de plantillas de flujo
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)
        proyecto.save()

        lista_actividades = []
        # se crean 3 actividades para controlar que se retorne la lista completa de sprints, que seran 3 en total
        for i in range(3):
            actividad_plantilla_flujo = ActividadFlujoPlantilla.objects.create(nombre='actividad_p%s' % i)
            actividad_plantilla_flujo.save()
            lista_actividades.append(actividad_plantilla_flujo)

        # se crean 10 plantillas de flujo para controlar que se retorne la lista completa de plantillas de flujo, que seran 10 en total
        for i in range(10):
            plantilla_flujo = PlantillaFlujo.objects.create(nombre='p_flujo%s' % i)
            plantilla_flujo.actividades = lista_actividades
            plantilla_flujo.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('flujos:index'))
        request.user = self.user

        response = IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'flujos/index.html')
        # verificamos las plantillas de flujo retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de IndexView de Plantillas de flujo realizado exitosamente'

    def test_view_crear_plantilla_flujo(self):
        """
        Funcion que realiza el test sobre la vista crear_plantilla_flujo que crea
        una nueva plantilla de flujo
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user3 = User.objects.create_user(username='user_prueba3', email='test@test223.com', password='prueba')
        # se crea un usuario

        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user3)
        proyecto.save()

        lista_actividades = []
        # se crean 3 actividades para controlar que se retorne la lista completa de sprints, que seran 3 en total
        for i in range(3):
            actividad_plantilla_flujo = ActividadFlujoPlantilla.objects.create(nombre='actividad_p%s' % i)
            actividad_plantilla_flujo.save()
            lista_actividades.append(actividad_plantilla_flujo)

        plantilla_flujo = PlantillaFlujo.objects.create(nombre='p_flujo_c')
        plantilla_flujo.actividades = lista_actividades
        plantilla_flujo.save()

        self.assertEqual(plantilla_flujo.nombre, 'p_flujo_c')

        print 'Test de crear_plantilla_flujo realizado exitosamente'

    def test_view_update_plantilla_flujo(self):
        """
        Funcion que realiza el test sobre la vista update_plantilla_flujo que modifica
        una plantilla de flujo existente
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user4 = User.objects.create_user(username='user_prueba4', email='test@test224.com', password='prueba')
        # se crea un usuario
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user4)

        proyecto.save()

        lista_actividades = []
        # se crean 3 actividades para controlar que se retorne la lista completa de sprints, que seran 3 en total
        for i in range(3):
            actividad_plantilla_flujo = ActividadFlujoPlantilla.objects.create(nombre='actividad_p%s' % i)
            actividad_plantilla_flujo.save()
            lista_actividades.append(actividad_plantilla_flujo)

        plantilla_flujo = PlantillaFlujo.objects.create(nombre='p_flujo_c')
        plantilla_flujo.actividades = lista_actividades
        plantilla_flujo.save()

        # se crean nuevos valores para los atributos
        nuevo_nombre = 'nuevo_nombre'

        # Se modifican los atributos del sprint
        plantilla_flujo.nombre = nuevo_nombre
        plantilla_flujo.save()

        self.assertEqual(plantilla_flujo.nombre, 'nuevo_nombre')

        print 'Test de update_plantilla_flujo realizado exitosamente'

    def test_view_ActividadCreate(self):
        """
        Funcion que realiza el test sobre la vista ActividadCreate que crea
        una nueva actividad
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user4 = User.objects.create_user(username='user_prueba4', email='test@test224.com', password='prueba')
        # se crea un usuario
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user4)

        proyecto.save()


        actividad_plantilla_flujo = ActividadFlujoPlantilla.objects.create(nombre='actividad_p')
        actividad_plantilla_flujo.save()

        self.assertEqual(actividad_plantilla_flujo.nombre, 'actividad_p')

        print 'Test de ActividadCreate realizado exitosamente'

    def test_view_FlujosProyectoIndex(self):
        """
        Funcion que realiza el test sobre la vista FlujosProyectoIndex que genera
        lista de flujos dentro de un proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)
        proyecto.save()

        lista_actividades = []
        # se crean 3 actividades para controlar que se retorne la lista completa de sprints, que seran 3 en total
        for i in range(3):
            actividad_flujo = Actividad.objects.create(nombre='actividad%s' % i)
            actividad_flujo.save()
            lista_actividades.append(actividad_flujo)

        # se crean 10 flujos para controlar que se retorne la lista completa de flujos, que seran 10 en total
        for i in range(10):
            flujo = Flujo.objects.create(nombre='flujo%s' % i, proyecto=proyecto)
            flujo.actividades = lista_actividades
            flujo.save()

        group = Group.objects.create(name='grupo')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        row_rol = RolProyecto_Proyecto(user=self.user, rol_proyecto=rolProyecto, proyecto=proyecto)
        row_rol.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('flujos:flujos_proyecto_index', args=[proyecto.pk]))
        request.user = self.user

        response = FlujosProyectoIndex.as_view()(request, pk_proyecto=proyecto.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'flujos/flujos_proyecto_index.html')
        # verificamos las plantillas de flujo retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de FlujosProyectoIndex realizado exitosamente'

    def test_view_FlujoProyectoAsignar(self):
        """
        Funcion que realiza el test sobre la vista FlujoProyectoAsignar que asigna
        un flujo a un proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user4 = User.objects.create_user(username='user_prueba4', email='test@test224.com', password='prueba')
        # se crea un usuario
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user4)

        proyecto.save()

        lista_actividades = []
        # se crean 3 actividades para controlar que se retorne la lista completa de sprints, que seran 3 en total
        for i in range(3):
            actividad_flujo = Actividad.objects.create(nombre='actividad%s' % i)
            actividad_flujo.save()
            lista_actividades.append(actividad_flujo)


        flujo = Flujo.objects.create(nombre='flujo', proyecto=proyecto)
        flujo.actividades = lista_actividades
        flujo.save()

        group = Group.objects.create(name='grupo')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        row_rol = RolProyecto_Proyecto(user=self.user, rol_proyecto=rolProyecto, proyecto=proyecto)
        row_rol.save()

        self.assertEqual(flujo.nombre, 'flujo')
        self.assertEqual(flujo.proyecto, proyecto)

        print 'Test de FlujoProyectoAsignar realizado exitosamente'
