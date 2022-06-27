from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Group, BaseGroup

admin.site.unregister(BaseGroup)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('__str__', 'real_name', 'student_id', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('real_name', 'student_id', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'real_name'),
        }),
    )


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass
