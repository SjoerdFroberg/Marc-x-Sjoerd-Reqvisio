from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

# Auto register all models in app
app = apps.get_app_config("procurement01")

for model_name, model in app.models.items():
    if model is not CustomUser:  # skip for double reg
        admin.site.register(model)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Display the company in the list view
    list_display = ("username", "email", "company", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "company__company_type")

    # Include the company field in the admin forms
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "company")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Include the company field in the user creation form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "company"),
            },
        ),
    )

    # Search and ordering
    search_fields = ("username", "email", "company__name")
    ordering = ("username",)
