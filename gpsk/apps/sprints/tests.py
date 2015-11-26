from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from models import Sprint
from views import IndexView, SprintBacklogIndexView, detalle_horas, TareasIndexView
from apps.proyectos.models import Proyecto
from apps.user_stories.models import UserStory, UserStoryDetalle, Tarea, Nota
from apps.flujos.models import Flujo, Actividad, Estado
from apps.roles_proyecto.models import RolProyecto, RolProyecto_Proyecto


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

        group = Group.objects.create(name='grupo')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        row_rol = RolProyecto_Proyecto(user=self.user, rol_proyecto=rolProyecto, proyecto=proyecto)
        row_rol.save()


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

        group = Group.objects.create(name='grupo')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        row_rol = RolProyecto_Proyecto(user=self.user, rol_proyecto=rolProyecto, proyecto=proyecto)
        row_rol.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('sprints:backlog', args=[proyecto.pk, sprint.pk]))
        request.user = self.user

        response = SprintBacklogIndexView.as_view()(request, pk_proyecto=proyecto.pk, pk_sprint=sprint.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'sprints/sprint_backlog.html')
        # verificamos los user stories retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de SprintBacklogIndexView de Sprints realizado exitosamente'

    def test_view_SprintGestionar(self):
        """
        Funcion que realiza el test sobre la vista SprintGestionar que despliega
        los user stories existentes para poder asignarlos al sprint
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()



        self.assertEqual(user_story.sprint, sprint)
        self.assertEqual(user_story.usuario, user4)

        print 'Test de SprintGestionar realizado exitosamente'

    def test_view_SprintAsignar(self):
        """
        Funcion que realiza el test sobre la vista SprintAsignar que asigna
        los user story a un sprint
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()


        self.assertEqual(user_story.sprint, sprint)
        self.assertEqual(user_story.usuario, user4)

        print 'Test de SprintAsignarGestionar realizado exitosamente'

    def test_view_SprintGestionarUpdate(self):
        """
        Funcion que realiza el test sobre la vista SprintGestionarUpdate que modifica la asignacion
        los user story a un sprint
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        user5 = User.objects.create_user(username='user_prueba5', email='test@test225.com', password='prueba')

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user5)
        user_story.save()

        self.assertEqual(user_story.sprint, sprint)
        self.assertEqual(user_story.usuario, user5)

        print 'Test de SprintGestionarUpdate realizado exitosamente'

    def test_view_detalle_horas(self):
        """
        Funcion que realiza el test sobre la vista detalle_horas que genera
        el detalle de los user stories del sprint y sus horas asignadas a los usuarios
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

        group = Group.objects.create(name='Developer')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('sprints:detalle_horas', args=[proyecto.pk, sprint.pk]))
        request.user = self.user
        view = detalle_horas
        response = view(request, pk_proyecto=proyecto.pk, pk_sprint=sprint.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de detalle_horas realizado exitosamente'

    def test_view_desasignar_user_story(self):
        """
        Funcion que realiza el test sobre la vista desasignar_user_story que desasigna
        un user story del sprint
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        user_story.estado = 'No asignado'
        user_story.usuario = None
        user_story.sprint = None
        user_story.save()

        self.assertEqual(user_story.estado, 'No asignado')
        self.assertEqual(user_story.sprint, None)
        self.assertEqual(user_story.usuario, None)

        print 'Test de desasignar_user_story realizado exitosamente'

    def test_view_iniciar_sprint(self):
        """
        Funcion que realiza el test sobre la funcion iniciar_sprint que inicia
        un sprint dado
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        sprint.estado = 'Activo'
        sprint.save()

        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        detalle = UserStoryDetalle(user_story=user_story, actividad=actividad, estado=estado)
        detalle.save()

        self.assertEqual(user_story, detalle.user_story)

        print 'Test de iniciar_sprint realizado exitosamente'

    def test_view_RegistarTarea(self):
        """
        Funcion que realiza el test sobre la vista RegistrarTarea que registra
        una tarea al user story
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        flujo = Flujo(nombre='flujo')
        flujo.save()

        tarea = Tarea.objects.create(user_story=user_story, descripcion='Una descripcion', horas_de_trabajo=20,
                                     actividad=actividad, estado=estado, sprint=sprint, flujo=flujo)
        tarea.save()

        self.assertEqual(tarea.user_story, user_story)
        self.assertEqual(tarea.descripcion, 'Una descripcion')
        self.assertEqual(tarea.horas_de_trabajo, 20)

        print 'Test de RegistrarTarea realizado exitosamente'

    def test_view_cambiar_estado(self):
        """
        Funcion que realiza el test sobre la vista cambiar estado que cambia
        el estado al user story
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        flujo = Flujo(nombre='flujo')
        flujo.save()

        tarea = Tarea.objects.create(user_story=user_story, descripcion='Una descripcion', horas_de_trabajo=20,
                                     actividad=actividad, estado=estado, sprint=sprint, flujo=flujo)
        tarea.save()

        actividad2 = Actividad(nombre='actividad2')
        actividad2.save()

        estado2 = Estado(nombre='estado2')
        estado2.save()

        detalle = UserStoryDetalle(user_story=user_story, actividad=actividad, estado=estado)
        detalle.save()

        detalle.actividad = actividad2
        detalle.estado = estado2
        detalle.save()

        self.assertEqual(detalle.actividad, actividad2)
        self.assertEqual(detalle.estado, estado2)

        print 'Test de cambiar_estado realizado exitosamente'

    def test_view_revertir_estado(self):
        """
        Funcion que realiza el test sobre la vista revertir estado que cambia
        el estado al user story a un estado anterior
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        flujo = Flujo(nombre='flujo')
        flujo.save()

        tarea = Tarea.objects.create(user_story=user_story, descripcion='Una descripcion', horas_de_trabajo=20,
                                     actividad=actividad, estado=estado, sprint=sprint, flujo=flujo)
        tarea.save()

        actividad2 = Actividad(nombre='actividad2')
        actividad2.save()

        estado2 = Estado(nombre='estado2')
        estado2.save()

        detalle = UserStoryDetalle(user_story=user_story, actividad=actividad, estado=estado)
        detalle.save()

        detalle.actividad = actividad2
        detalle.estado = estado2
        detalle.save()

        detalle.actividad = actividad
        detalle.estado = estado
        detalle.save()

        self.assertEqual(detalle.actividad, actividad)
        self.assertEqual(detalle.estado, estado)

        print 'Test de revertir_estado realizado exitosamente'

    def test_view_aprobar_user_story(self):
        """
        Funcion que realiza el test sobre la vista aprobar_user_story que aprueba
        un user story finalizado
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        flujo = Flujo(nombre='flujo')
        flujo.save()

        tarea = Tarea.objects.create(user_story=user_story, descripcion='Una descripcion', horas_de_trabajo=20,
                                     actividad=actividad, estado=estado, sprint=sprint, flujo=flujo)
        tarea.save()

        user_story.estado = 'Aprobado'
        user_story.save()

        self.assertEqual(user_story.estado, 'Aprobado')

        print 'Test de aprobar_user_story realizado exitosamente'

    def test_view_finalizar_sprint(self):
        """
        Funcion que realiza el test sobre la funcion finalizar_sprint que finaliza
        un sprint dado
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        sprint.estado = 'Finalizado'
        sprint.save()

        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        detalle = UserStoryDetalle(user_story=user_story, actividad=actividad, estado=estado)
        detalle.save()

        self.assertEqual(user_story, detalle.user_story)

        print 'Test de finalizar_sprint realizado exitosamente'

    def test_view_TareasIndexView(self):
        """
        Funcion que realiza el test sobre la vista TareasIndexView que genera
        lista de tareas del user stories del sprint
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=2, proyecto=proyecto, sprint=sprint)
        user_story.save()

        group = Group.objects.create(name='grupo')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        row_rol = RolProyecto_Proyecto(user=self.user, rol_proyecto=rolProyecto, proyecto=proyecto)
        row_rol.save()


        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        flujo = Flujo(nombre='flujo')
        flujo.save()

        for i in range(10):
            tarea = Tarea.objects.create(user_story=user_story, descripcion='Una descripcion', horas_de_trabajo=20,
                                         actividad=actividad, estado=estado, sprint=sprint, flujo=flujo)
            tarea.save()

        self.assertEqual(tarea.user_story, user_story)
        self.assertEqual(tarea.descripcion, 'Una descripcion')
        self.assertEqual(tarea.horas_de_trabajo, 20)

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('sprints:ver_tareas', args=[proyecto.pk, sprint.pk, user_story.pk]))
        request.user = self.user

        response = TareasIndexView.as_view()(request, pk_proyecto=proyecto.pk, pk_sprint=sprint.pk, pk_user_story=user_story.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'sprints/ver_tareas.html')
        # verificamos los user stories retornados
        self.assertEqual(len(response.context_data['object_list']), 10)

        print 'Test de TareasIndexView de Sprints realizado exitosamente'

    def test_view_AgregarNota(self):
        """
        Funcion que realiza el test sobre la vista AgregarNota que registra
        una nota al user story
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        actividad = Actividad(nombre='actividad')
        actividad.save()

        estado = Estado(nombre='estado')
        estado.save()

        flujo = Flujo(nombre='flujo')
        flujo.save()

        nota = Nota.objects.create(user_story=user_story, texto='texto', usuario=user4)
        nota.save()

        self.assertEqual(nota.user_story, user_story)
        self.assertEqual(nota.texto, 'texto')
        self.assertEqual(nota.usuario, user4)

        print 'Test de AgregarNota realizado exitosamente'

    def test_view_descartar_user_story(self):
        """
        Funcion que realiza el test sobre la vista descartar_user_story que descarta
        un user story del sprint
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

        user_story = UserStory.objects.create(nombre='us', descripcion='desc',
                                              valor_negocio=20, proyecto=proyecto, sprint=sprint, usuario=user4)
        user_story.save()

        user_story.estado = 'Descartado'

        user_story.save()

        self.assertEqual(user_story.estado, 'Descartado')

        print 'Test de descartar_user_story realizado exitosamente'

    def test_view_burndown_chart(self):
        """
        Funcion que realiza el test sobre la vista burndown_chart que genera
        el burndown chart del sprint
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

        group = Group.objects.create(name='Developer')
        group.save()
        rolProyecto = RolProyecto(group=group, es_rol_proyecto=True)
        rolProyecto.save()

        # verificamos que la vista devuelva el template adecuado
        request = self.factory.get(reverse('sprints:burndown_chart', args=[proyecto.pk, sprint.pk]))
        request.user = self.user
        view = detalle_horas
        response = view(request, pk_proyecto=proyecto.pk, pk_sprint=sprint.pk)
        self.assertEqual(response.status_code, 200)

        print 'Test de burndown_chart realizado exitosamente'

