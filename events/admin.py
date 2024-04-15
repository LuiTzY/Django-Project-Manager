from django.contrib import admin
from .models import ProyectHistorial
# Register your models here.
class ProyectHistorialAdmin(admin.ModelAdmin):
    readonly_fields = ('action','timestamp')
