from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import update_session_auth_hash
from forms import UserProfileForm, MyPasswordChangeForm
from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_done, \
    password_reset_complete



@login_required(login_url='/login/')
def home(request):
    """
    Genera la vista home del sistema.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @rtype: django.http.HttpResponse
    @return: Renderiza index.html, la pagina de inicio del sistema
    """
    template = 'index.html'
    return render(request, template, locals())


def custom_login(request):
    """
    Genera la vista de login al sistema.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza login.html si el usuario no esta autenticado o
            redirecciona a la vista home si el usuario esta autenticado.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return login(request, template_name='login.html')


def reset(request):
    return password_reset(request, template_name='password_reset_form.html',
                          email_template_name='password_reset_email.html',
                          subject_template_name='password_reset_subject.txt',
                          post_reset_redirect=reverse('reset_done'))


def reset_done(request):
    return password_reset_done(request, template_name='password_reset_done.html')


def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='password_reset_confirm.html',
                                  uidb64=uidb64, token=token,
                                  post_reset_redirect=reverse('reset_complete'))


def reset_complete(request):
    return password_reset_complete(request, template_name='password_reset_complete.html')


@login_required(login_url='/login/')
def user_profile(request):
    usuario = request.user
    if request.method == 'POST':


        form = UserProfileForm(request.POST, instance=usuario)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = UserProfileForm(instance=usuario)

    return render(request, 'mi_perfil.html', locals())


@login_required(login_url='/login/')
def perfil_change_password(request):
    """
    Funcion que permite modificar el password del usuario actual.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_usuario: string
    @param pk_usuario: id del usuario con password a modificar

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza perfil_password_change.html para obtener el formulario o
            redirecciona a la vista home del sistema.
    """
    if request.method == 'POST':
        user_detail = get_object_or_404(User, pk=request.user.id)
        form = MyPasswordChangeForm(user_detail, request.POST)
        if form.is_valid():
            new_user = form.save()
            update_session_auth_hash(request, user_detail)
            return HttpResponseRedirect(reverse( 'user_profile'))
    else:
        user_detail = get_object_or_404(User, pk=request.user.id)
        form = MyPasswordChangeForm(user_detail)

    return render(request, 'perfil_password_change.html', locals())
