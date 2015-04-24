from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from models import Sprint
from views import IndexView, SprintBacklogIndexView
from apps.proyectos.models import Proyecto
from apps.user_stories.models import UserStory


class SprintsTest(TestCase):
    """
    Clase que realiza el Test del modulo de administracion de sprints
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
        lista de sprints
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)
        proyecto.save()

        # se crean 10 sprints para controlar que se retorne la lista completa de sprints, que seran 10 en total
        for i in range(10):
            sprint = Sprint.objects.create(nombre='sprint%s' % i, duracion='%d' % i, proyecto=proyecto)
            sprint.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('sprints:index', args=[proyecto.pk]))
        request.user = self.user

        response = IndexView.as_view()(request, pk_proyecto=proyecto.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'sprints/index.html')
        # verificamos los user stories retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de IndexView de Sprints realizado exitosamente'

    def test_view_SprintCreate(self):
        """
        Funcion que realiza el test sobre la vista SprintCreate que crea
        un nuevo sprint
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user3 = User.objects.create_user(username='user_prueba3', email='test@test223.com', password='prueba')
        # se crea un usuario

        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user3)
        proyecto.save()

        sprint = Sprint.objects.create(nombre='sprint', duracion=15, proyecto=proyecto)
        sprint.save()

        self.assertEqual(sprint.nombre, 'sprint')
        self.assertEqual(sprint.duracion, 15)

        print 'Test de SprintCreate realizado exitosamente'

    def test_view_SprintUpdate(self):
        """
        Funcion que realiza el test sobre la vista SprintUpdate que modifica
        un sprint existente
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user4 = User.objects.create_user(username='user_prueba4', email='test@test224.com', password='prueba')
        # se crea un usuario
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user4)

        proyecto.save()

        sprint = Sprint.objects.create(nombre='sprint', duracion=15, proyecto=proyecto)
        sprint.save()

        # se crean nuevos valores para los atributos
        nueva_duracion = 5
        nuevo_nombre = 'nuevo_nombre'

        # Se modifican los atributos del sprint
        sprint.duracion = nueva_duracion
        sprint.nombre = nuevo_nombre
        sprint.save()

        self.assertEqual(sprint.duracion, 5)
        self.assertEqual(sprint.nombre, 'nuevo_nombre')

        print 'Test de SprintUpdate realizado exitosamente'

    def test_view_SprintBacklogIndexView(self):
        """
        Funcion que realiza el test sobre la vista SprintBacklogIndexView que genera
        lista de user stories del sprint
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)
        proyecto.save()

        sprint = Sprint.objects.create(nombre='sprint', duracion=15, proyecto=proyecto)
        sprint.save()

        # se crean 10 user stories para controlar que se retorne la lista completa, que seran 10 en total
        for i in range(10):
            user_story = UserStory.objects.create(nombre='us%s' % i, descripcion='desc%s' % i,
                                                  valor_negocio='%d' % i, proyecto=proyecto, sprint=sprint)
            user_story.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('sprints:backlog', args=[proyecto.pk, sprint.pk]))
        request.user = self.user

        response = SprintBacklogIndexView.as_view()(request, pk_proyecto=proyecto.pk, pk_sprint=sprint.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'sprints/sprint_backlog.html')
        # verificamos los user stories retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de SprintBacklogIndexView de Sprints realizado exitosamente'