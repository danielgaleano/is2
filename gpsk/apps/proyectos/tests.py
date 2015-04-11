import datetime
from django.test import TestCase
from django.test.client import RequestFactory

from django.contrib.auth.models import User
from models import Proyecto
from views import IndexView


class ProyectosTest(TestCase):
    """
    Clase que realiza el Test del modulo de administracion de proyectos
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
        Funcion que realiza el test sobre la vista UserIndexView que genera
        lista de usuarios
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')
        # se crean 10 proyectos para controlar que se retorne la lista completa de usuarios, que seran 11 en total
        for i in range(10):
            proyecto = Proyecto.objects.create(codigo='co%s' % i, nombre_corto='test%s' % i,
                                               nombre_largo='test%s' % i, cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get('/proyectos/')
        view = IndexView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'proyectos/index.html')
        # verificamos los usuarios retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de IndexView de Proyecto realizado exitosamente'

    def test_view_ProyectoCreate(self):
        """
        Funcion que realiza el test sobre la vista ProyectoCreate que crea
        un nuevo usuario
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user3 = User.objects.create_user(username='user_prueba3', email='test@test223.com', password='prueba')
        # se crea un usuario
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user3)

        self.assertEqual(proyecto.codigo, 'codi')
        self.assertEqual(proyecto.nombre_corto, 'test')

        print 'Test de ProyectoCreate realizado exitosamente'

    def test_view_ProyectoUpdate(self):
        """
        Funcion que realiza el test sobre la vista ProyectoUpdate que modifica
        un usuario existente
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user4 = User.objects.create_user(username='user_prueba4', email='test@test224.com', password='prueba')
        # se crea un usuario
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user4)

        # se crean nuevos valores para los atributos
        nuevo_codigo = 'new'
        new_nombre = 'Hola'

        # Se modifican los atributos del usuario
        proyecto.codigo = nuevo_codigo
        proyecto.nombre_corto = new_nombre
        proyecto.save()

        self.assertEqual(proyecto.codigo, 'new')
        self.assertEqual(proyecto.nombre_corto, 'Hola')

        print 'Test de ProyectoUpdate realizado exitosamente'

    def test_view_cancelar_proyecto(self):
        """
        Funcion que realiza el test sobre la vista proyecto que cambia el estado
        de un proyecto a cancelado
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user5 = User.objects.create_user(username='user_prueba5', email='test@test225.com', password='prueba')
        # se crea un usuario
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user5)
        # se marca al proyecto
        proyecto.cancelado = True
        proyecto.save()

        self.assertEqual(proyecto.cancelado, True)

        print 'Test de cancelarProyecto realizado exitosamente'
