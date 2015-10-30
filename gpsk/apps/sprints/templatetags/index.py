from django import template
from django.contrib.auth.models import Permission
register = template.Library()


@register.filter
def index(List, i):
    return List[int(i)]


@register.filter(name='tiene_permiso')
def tiene_permiso(lista, permiso):
    el_permiso = Permission.objects.get(codename=permiso)
    print "El permiso templatetag %s" % el_permiso
    tiene = False
    print lista
    if el_permiso in lista:
        tiene = True

    return tiene