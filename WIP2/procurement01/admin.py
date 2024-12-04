from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Company, CustomUser, RFX, GeneralQuestion, RFX_SKUs, SKUSpecificQuestion, RFXFile, RFXInvitation, SupplierResponse, SKUSpecificQuestionResponse, GeneralQuestionResponse, RFX_SKUSpecificationData


admin.site.register(Company)

admin.site.register(RFX)
admin.site.register(GeneralQuestion)
admin.site.register(RFX_SKUs)
admin.site.register(SKUSpecificQuestion)
admin.site.register(RFXFile)
admin.site.register(RFXInvitation)
admin.site.register(SupplierResponse)
admin.site.register(SKUSpecificQuestionResponse)
admin.site.register(GeneralQuestionResponse)
admin.site.register(RFX_SKUSpecificationData)


# Register your CustomUser model with UserAdmin to get all the features

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Display the company in the list view
    list_display = ('username', 'email', 'company', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'company__company_type')

    # Include the company field in the admin forms
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'company')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Include the company field in the user creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'company'),
        }),
    )

    # Search and ordering
    search_fields = ('username', 'email', 'company__name')
    ordering = ('username',)