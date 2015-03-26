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
        """
        Funcion que inicializa el RequestFactory y un usuario de prueba para
        realizar los test
        """
        # Se crea el Request factory pars simular peticiones
        self.factory = RequestFactory()
        # Se crea el User que realiza las peticiones
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='test')

    def test_view_UserIndexView(self):
        """
        Funcion que realiza el test sobre la vista UserIndexView que genera
        lista de usuarios
        """
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

        print 'Test de UserIndexView realizado exitosamente'

    def test_view_UserCreate(self):
        """
        Funcion que realiza el test sobre la vista UserCreate que crea
        un nuevo usuario
        """
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
        """
        Funcion que realiza el test sobre la vista UserUpdate que modifica
        un usuario existente
        """
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

    def test_view_inactivar_usuario(self):
        """
        Funcion que realiza el test sobre la vista inactivar_usuario que cambia el estado
        de un usuario a inactivo
        """
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

        print 'Test de inactivar_usuario realizado exitosamente'

    def test_view_activar_usuario(self):
        """
        Funcion que realiza el test sobre la vista activar_usuario que cambia el estado
        de un usuario a activo
        """
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
        # se marca al usuario como activo
        usuario_prueba.user.is_active = True
        usuario_prueba.save()

        self.assertEqual(usuario_prueba.user.is_active, True)

        print 'Test de activar_usuario realizado exitosamente'
