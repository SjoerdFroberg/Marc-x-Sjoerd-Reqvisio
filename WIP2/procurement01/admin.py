from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Company, CustomUser, RFP, GeneralQuestion, RFP_SKUs

# Register your models here.


admin.site.register(Company)

admin.site.register(RFP)
admin.site.register(GeneralQuestion)
admin.site.register(RFP_SKUs)


# Register your CustomUser model with UserAdmin to get all the features
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # You can customize the admin view for your custom user model here
    pass