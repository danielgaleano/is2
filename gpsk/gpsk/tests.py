from django.test import TestCase
from django.test.client import RequestFactory

from django.contrib.auth.models import User


class AutenticationTest(TestCase):
    """
    Clase que realiza el Test del modulo de autenticacion de usuarios
    """

    def setUp(self):
        # Se crea el Request factory pars simular peticiones
        self.factory = RequestFactory()
        # Se crea el User que realiza las peticiones
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='test')

    def test_login_user_exist(self):
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        # se verifica la redireccion a /
        response = self.client.get('/login/')
        self.assertRedirects(response, expected_url='/', status_code=302, target_status_code=200)

        print 'Test de login_user_exist realizado exitosamente'

    def test_login_user_not_exist(self):
        # se loguea un usuario que no existe
        user = self.client.login(username='noexiste', password='no')
        self.assertFalse(user)

        print 'Test de login_user_not_exist realizado exitosamente'

    def test_logout(self):
        # cierra session
        user = self.client.logout()
        self.assertFalse(user)

        # verificamos que el usuario es redirigido al login al intentar ingresar a usuarios
        response=self.client.get("/usuarios/")
        self.assertRedirects(response,'/login/?next=/usuarios/')

        print 'Test de logout realizado exitosamente'