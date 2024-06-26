from django.contrib import admin
from .models import Proyect,Task,Member

"""
    Aqui se registran los modelos que se mostraran en el panel de administracion, con las configuraciones 
"""
class ProyectAdmin(admin.ModelAdmin):
    #esto hace que al guardar un proyecto se asigne al usuario que esta en la request
    def save_model(self, request, obj, form, change):
        if 'project_owner' not in form.cleaned_data or form.cleaned_data['project_owner'] is None:
            obj.project_owner = request.user
        obj.save()
    #campos de lectura, filtrado    
    readonly_fields = ("created_at","update_at")
    search_fields = ('project_name','proyect_objetive','project_owner__email')
    list_display = ('created_at','update_at')
    
class TaskAdmin(admin.ModelAdmin):
    #campos de lectura, filtrado
    readonly_fields = ("created_at","update_at")
    search_fields = ('title','description','completed','asigned_at__email')
    list_display = ('created_at','datecompleted')
    list_filter = ('completed',)
    
class MemberAdmin(admin.ModelAdmin):
    #campos de lectura, filtrado
    readonly_fields = ("joined_at",)
    search_fields = ('proyect','joined_at','user__email',)
    list_filter = ('proyect','joined_at')

#se registran estas configuraciones    
admin.site.register(Proyect,ProyectAdmin)
admin.site.register(Task)
admin.site.register(Member, MemberAdmin)
