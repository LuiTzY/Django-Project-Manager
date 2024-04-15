from django.contrib import admin
from .models import Proyect,Task,Member

# Register your models here.
class ProyectAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if 'project_owner' not in form.cleaned_data or form.cleaned_data['project_owner'] is None:
            obj.project_owner = request.user
        obj.save()

admin.site.register(Proyect,ProyectAdmin)
admin.site.register(Task)
admin.site.register(Member)
