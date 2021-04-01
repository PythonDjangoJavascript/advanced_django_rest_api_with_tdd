from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Modefy default admin user fields in admin page"""

    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        # Here None is for the title section
        (None, {
            "fields": (
                "email",
                "password"
            ),
        }),
        (_("Personal Info"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser"
            ),
        }),
        (_("Important Dates"), {
            "fields": (
                "last_login",
            ),
        })
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2")
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
