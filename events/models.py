from django.db import models

class ProyectHistorial(models.Model):
    action = models.CharField(max_length=100, verbose_name="Acción")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha en la que ocurrio")
    class Meta:
        verbose_name = "HistorialProyecto"
        verbose_name_plural = "HistorialProyectos"