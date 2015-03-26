from django.test import TestCase
from django.test.client import RequestFactory

from django.contrib.auth.models import User
from views import UserIndexView
from models import Usuario


class UsuariosTest(TestCase):
    """
    Clase que realiza el Test del modulo de administracion de usuarios
    """
    def setUp(self):
        # Se crea el Request factory pars simular peticiones
        self.factory = RequestFactory()
        # Se crea el User que realiza las peticiones
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='test')

    def test_view_UserIndexView(self):
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        # se crean 10 Usuarios para controlar que se retorne la lista completa de usuarios, que seran 11 en total
        for i in range(10):
            user = User.objects.create_user(username='usuario%s' % i, email='test%s@test.com' % i, password='test')
            Usuario.objects.create(user=user, telefono='tel%s' % i, direccion="dir%s" % i)

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get('/usuarios/')
        view = UserIndexView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'usuarios/index.html')
        # verificamos los usuarios retornados
        self.assertEqual(len(response.context_data['object_list']), 11)

        print 'Test de IndexView realizado exitosamente'

    def test_view_UserCreate(self):
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        # se crea un usuario
        user = User.objects.create_user(username='user_prueba', email='test@test.com', password='prueba')
        Usuario.objects.create(user=user, telefono='222', direccion='Avenida')

        self.assertEqual(Usuario.objects.get(user=user).user.username, 'user_prueba')
        self.assertEqual(Usuario.objects.get(user=user).user.email, 'test@test.com')
        self.assertEqual(Usuario.objects.get(user=user).telefono, '222')

        print 'Test de UserCreate realizado exitosamente'

    def test_view_UserUpdate(self):
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        # se crea un usuario
        user = User.objects.create_user(username='user_prueba', email='test@test.com', password='prueba')
        usuario_prueba = Usuario.objects.create(user=user, telefono='222', direccion='Avenida')

        # se crean nuevos valos para los atributos
        nuevo_username = 'new_name'
        new_tel = '333'
        new_email = 'newemail@new.com'
        # Se modifican los atributos del usuario
        usuario_prueba.user.username = nuevo_username
        usuario_prueba.telefono = new_tel
        usuario_prueba.user.email = new_email
        usuario_prueba.save()

        self.assertEqual(usuario_prueba.user.username, 'new_name')
        self.assertEqual(usuario_prueba.user.email, 'newemail@new.com')
        self.assertEqual(usuario_prueba.telefono, '333')

        print 'Test de UserUpdate realizado exitosamente'

    def test_view_eliminar_usuario(self):
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        # se crea un usuario
        user = User.objects.create_user(username='user_prueba', email='test@test.com', password='prueba')
        usuario_prueba = Usuario.objects.create(user=user, telefono='222', direccion='Avenida')
        # se marca al usuario como inactivo
        usuario_prueba.user.is_active = False
        usuario_prueba.save()

        self.assertEqual(usuario_prueba.user.is_active, False)

        print 'Test de eliminar_usuario realizado exitosamente'
