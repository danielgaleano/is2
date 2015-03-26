from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from models import Usuario


class UsuarioInline(admin.StackedInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Usuario informacion adicional'


class UserAdmin(UserAdmin):
    inlines = (UsuarioInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
