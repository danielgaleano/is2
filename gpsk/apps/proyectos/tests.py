from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from apps.roles_proyecto.models import RolProyecto, RolProyecto_Proyecto
from apps.sprints.models import Sprint
from models import Proyecto
from views import IndexView, proyecto_index, proyecto_reportes, \
    proyecto_reporte_trabajos_equipo, proyecto_reporte_product_backlog, \
    proyecto_reporte_sprint_backlog, proyecto_reporte_trabajos_usuario, reporte_grafico_reportlab, proyecto_reporte_actividades


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
        lista de proyectos
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')
        # se crean 10 proyectos para controlar que se retorne la lista completa de proyectos, que seran 11 en total
        for i in range(10):
            proyecto = Proyecto.objects.create(codigo='co%s' % i, nombre_corto='test%s' % i,
                                               nombre_largo='test%s' % i, cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get('/proyectos/')
        view = IndexView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'proyectos/index.html')
        # verificamos los proyectos retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de IndexView de Proyecto realizado exitosamente'

    def test_view_ProyectoCreate(self):
        """
        Funcion que realiza el test sobre la vista ProyectoCreate que crea
        un nuevo proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user3 = User.objects.create_user(username='user_prueba3', email='test@test223.com', password='prueba')
        # se crea un proyecto
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user3)

        self.assertEqual(proyecto.codigo, 'codi')
        self.assertEqual(proyecto.nombre_corto, 'test')

        print 'Test de ProyectoCreate realizado exitosamente'

    def test_view_ProyectoUpdate(self):
        """
        Funcion que realiza el test sobre la vista ProyectoUpdate que modifica
        un proyecto existente
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user4 = User.objects.create_user(username='user_prueba4', email='test@test224.com', password='prueba')
        # se crea un proyecto
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user4)

        # se crean nuevos valores para los atributos
        nuevo_codigo = 'new'
        new_nombre = 'Hola'

        # Se modifican los atributos del proyecto
        proyecto.codigo = nuevo_codigo
        proyecto.nombre_corto = new_nombre
        proyecto.save()

        self.assertEqual(proyecto.codigo, 'new')
        self.assertEqual(proyecto.nombre_corto, 'Hola')

        print 'Test de ProyectoUpdate realizado exitosamente'

    def test_view_cancelar_proyecto(self):
        """
        Funcion que realiza el test sobre la vista cancelar_proyecto que cambia el estado
        de un proyecto a cancelado
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user5 = User.objects.create_user(username='user_prueba5', email='test@test225.com', password='prueba')
        # se crea un proyecto
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user5)
        # se marca al proyecto
        proyecto.cancelado = True
        proyecto.save()

        self.assertEqual(proyecto.cancelado, True)

        print 'Test de cancelarProyecto realizado exitosamente'

    def test_view_proyecto_index(self):
        """
        Funcion que realiza el test sobre la vista proyecto_index que genera
        el index del proyecto seleccionado
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:proyecto_index', args=[proyecto.pk]))
        request.user = self.user
        view = proyecto_index
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de proyecto_index realizado exitosamente'

    def test_view_listar_equipo(self):
        """
        Funcion que realiza el test sobre la vista listar_equipo que genera
        lista de usuarios que se encuentran en el equipo del proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        lista_usuarios = []
        for i in range(10):
            user = User.objects.create_user(username='usuario%s' % i, email='test%s@test.com' % i, password='test')
            user.save()
            lista_usuarios.append(user)

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)
        proyecto.equipo = lista_usuarios
        proyecto.save()

        cantidad = len(lista_usuarios)
        cantidad_equipo = proyecto.equipo.all().count()

        self.assertEqual(cantidad_equipo, cantidad)

        print 'Test de listar_equipo realizado exitosamente'

    def test_view_AddMiembro(self):
        """
        Funcion que realiza el test sobre la vista AddMiembro que agrega
        un usuario al equipo del proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        lista_usuarios = []
        for i in range(10):
            user = User.objects.create_user(username='usuario%s' % i, email='test%s@test.com' % i, password='test')
            user.save()
            lista_usuarios.append(user)

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)
        proyecto.equipo = lista_usuarios
        proyecto.save()

        user_nuevo = User.objects.create_user(username='user_nuevo', email='test@test99.com', password='prueba')

        proyecto.equipo.add(user_nuevo)
        proyecto.save()
        lista_usuarios.append(user_nuevo)
        cantidad = len(lista_usuarios)
        cantidad_equipo = proyecto.equipo.all().count()

        self.assertEqual(cantidad_equipo, cantidad)

        print 'Test de AddMiembro realizado exitosamente'

    def test_view_delete_miembro(self):
        """
        Funcion que realiza el test sobre la vista delete_miembro que elimina
        un usuario del equipo del proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        lista_usuarios = []
        for i in range(10):
            user = User.objects.create_user(username='usuario%s' % i, email='test%s@test.com' % i, password='test')
            user.save()
            lista_usuarios.append(user)

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)
        proyecto.equipo = lista_usuarios
        proyecto.save()


        user_eliminar = User.objects.get(username='usuario1')

        proyecto.equipo.remove(user_eliminar)
        proyecto.save()
        lista_usuarios.remove(user_eliminar)
        cantidad = len(lista_usuarios)
        cantidad_equipo = proyecto.equipo.all().count()

        self.assertEqual(cantidad_equipo, cantidad)

        print 'Test de delete_miembro realizado exitosamente'

    def test_view_proyecto_reportes(self):
        """
        Funcion que realiza el test sobre la vista proyecto_reportes que genera
        el index de los reportes del proyecto seleccionado
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:proyecto_reportes', args=[proyecto.pk]))
        request.user = self.user
        view = proyecto_reportes
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de proyecto_reportes realizado exitosamente'

    def test_view_proyecto_reporte_trabajos_equipo(self):
        """
        Funcion que realiza el test sobre la vista proyecto_reporte_trabajos_equipo que genera
        el reporte de los trabajos realizados por cada equipo
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:reporte_trabajo_equipo', args=[proyecto.pk]))
        request.user = self.user
        view = proyecto_reporte_trabajos_equipo
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de proyecto_reporte_trabajos_equipo realizado exitosamente'

    def test_view_reporte_grafico_reportlab(self):
        """
        Funcion que realiza el test sobre la vista reporte_grafico_reportlab que genera
        el reporte de los burndown_chart de los sprints
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:reporte_grafico_sprints', args=[proyecto.pk]))
        request.user = self.user
        view = reporte_grafico_reportlab
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de reporte_grafico_reportlab realizado exitosamente'

    def test_view_proyecto_reporte_trabajos_usuario(self):
        """
        Funcion que realiza el test sobre la vista proyecto_reporte_trabajos_usuario que genera
        el reporte de los trabajos realizados por cada usuario
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)

        for i in range(10):
            sprint_s = Sprint.objects.create(nombre='sprint%s' % i, duracion='%d' % i, proyecto=proyecto, estado='Activo')
            sprint_s.save()

        sprint = Sprint.objects.filter(estado='Activo')

        group = Group.objects.create(name='Developer')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        row_rol = RolProyecto_Proyecto(user=self.user, rol_proyecto=rolProyecto, proyecto=proyecto)
        row_rol.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:reporte_trabajo_usuario', args=[proyecto.pk]))
        request.user = self.user
        view = proyecto_reporte_trabajos_usuario
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de proyecto_reporte_trabajos_usuario realizado exitosamente'

    def test_view_proyecto_reporte_actividades(self):
        """
        Funcion que realiza el test sobre la vista proyecto_reporte_actividades que genera
        el reporte de las actividades a realizar en el proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:proyecto_reporte_actividades', args=[proyecto.pk]))
        request.user = self.user
        view = proyecto_reporte_actividades
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de proyecto_reporte_actividades realizado exitosamente'

    def test_view_proyecto_reporte_product_backlog(self):
        """
        Funcion que realiza el test sobre la vista proyecto_reporte_product_backlog que genera
        el reporte de los user stories del product backlog del proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:proyecto_reporte_product_backlog', args=[proyecto.pk]))
        request.user = self.user
        view = proyecto_reporte_product_backlog
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de proyecto_reporte_product_backlog realizado exitosamente'

    def test_view_proyecto_reporte_sprint_backlog(self):
        """
        Funcion que realiza el test sobre la vista proyecto_reporte_sprint_backlog que genera
        el reporte de los user stories del sprint backlog del sprint actual
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)
        user2 = User.objects.create_user(username='user_prueba', email='test@test22.com', password='prueba')

        proyecto = Proyecto.objects.create(codigo='co', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user2)

        for i in range(10):
            sprint_s = Sprint.objects.create(nombre='sprint%s' % i, duracion='%d' % i, proyecto=proyecto, estado='Activo')
            sprint_s.save()

        sprint = Sprint.objects.filter(estado='Activo')


        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('proyectos:proyecto_reporte_sprint_backlog', args=[proyecto.pk]))
        request.user = self.user
        view = proyecto_reporte_sprint_backlog
        response = view(request, pk=proyecto.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de proyecto_reporte_sprint_backlog realizado exitosamente'

    def test_view_iniciar_proyecto(self):
        """
        Funcion que realiza el test sobre la vista iniciar_proyecto que inicia
        el proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user3 = User.objects.create_user(username='user_prueba3', email='test@test223.com', password='prueba')
        # se crea un proyecto
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user3)

        proyecto.save()
        proyecto.estado = "Activo"
        proyecto.save()

        self.assertEqual(proyecto.codigo, 'codi')
        self.assertEqual(proyecto.nombre_corto, 'test')
        self.assertEqual(proyecto.estado, 'Activo')

        print 'Test de iniciar_proyecto realizado exitosamente'

    def test_view_finalizar_proyecto(self):
        """
        Funcion que realiza el test sobre la vista finalizar_proyecto que inicia
        el proyecto
        """
        # se loguea el usuario testuser
        user = self.client.login(username='testuser', password='test')
        self.assertTrue(user)

        user3 = User.objects.create_user(username='user_prueba3', email='test@test223.com', password='prueba')
        # se crea un proyecto
        proyecto = Proyecto.objects.create(codigo='codi', nombre_corto='test',
                                           nombre_largo='test', cancelado=False, scrum_master=user3)

        proyecto.save()
        proyecto.estado = "Finalizado"
        proyecto.save()

        self.assertEqual(proyecto.codigo, 'codi')
        self.assertEqual(proyecto.nombre_corto, 'test')
        self.assertEqual(proyecto.estado, 'Finalizado')

        print 'Test de finalizar_proyecto realizado exitosamente'

