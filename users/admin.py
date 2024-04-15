from django.contrib import admin
from .models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at","update_at")
    search_fields = ("first_name","email")
    list_filter = ("user_admin",)
    
admin.site.register(User,UserAdmin)

