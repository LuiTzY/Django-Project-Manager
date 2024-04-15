from django.db import models

# Create your models here.
from django.db import models
from proyects.models import Member

class LoginEvent(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Usuario Logueado")
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

class ProyectEvent(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Usuario Logueado")
    action = models.CharField(max_length=100)
    timestamp = models.DateField(auto_now_add=True)

class ProyectHistorial(models.Model):
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)