from django.contrib import admin
from .models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    
    readonly_fields = ("created_at","update_at")
    search_fields = ("first_name","email")
    list_filter = ("user_admin",)
    
admin.site.register(User,UserAdmin)

title = "Gestionador de Proyectos"
sub_title = "Panel de gestion"
#Representa el titulo del panel de administracion
admin.site.site_header = title
#Representa el titulo de la pagina del panel de administracion
admin.site.site_title = title
#Representa el subtitulo que se encuentra en el panel de administracion
admin.site.index_title = sub_title