from django.db import models
from users.models import User
from django.shortcuts import get_list_or_404

class Proyect(models.Model):
    project_name = models.CharField(max_length = 40, verbose_name = "Nombre Proyecto")
    project_description = models.TextField(verbose_name="Descripcion del proyecto")
    proyect_objetive = models.TextField(verbose_name="Objetivo del proyecto")
    project_owner = models.ForeignKey(User, verbose_name = "Usuario",editable=False, on_delete = models.CASCADE, related_name="proyectos_creador")
    created_at = models.DateField(auto_now_add=True, verbose_name="Creado el ")
    update_at = models.DateField(auto_now = True, verbose_name = "Actualizado el")
    
    def __str__(self):
        return f"{self.project_name} created by {self.project_owner}"
    
    def get_available_members(self):
        return User.objects.exclude(id=self.project_owner.id)


class Member(models.Model):
    #Un miembro va a pertenecer a un usuario, EL RELATED_NAME ES PARA IDENTIFICAR A LOS PROYECTOS QUE EL USUARIO ES MIEMBRO
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    #Un miembro va a pertenecer a un proyecto
    proyect = models.ForeignKey(Proyect, on_delete=models.CASCADE, related_name="proyectos_miembros")
    is_admin = models.BooleanField(default=False, verbose_name="Rol de Admin")
    joined_at = models.DateField(auto_now=True, verbose_name="Unido el",blank= True)

    def __str__(self) :
        return f"{self.user.first_name} - {self.proyect}"

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    #Esto es una relacion de que esta tarea esta relacionada a un proyecto en si
    proyect = models.ForeignKey(Proyect, on_delete=models.CASCADE, related_name='tareas')
    #La tarea es asginada a un usuario especifico, el related name hace que desde el modelo con el que se relacione
    #pueda acceder a ese campo con el related_name que le coloco, es una relacion inversa
    completed = models.BooleanField(default=False, verbose_name="Completa")
    important = models.BooleanField(default=False,verbose_name="Importancia de la tarea")
    datecompleted = models.DateTimeField(null=True,blank=True, verbose_name="Completa el")

    asigned_at = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='tareas_asignadas')
    created_at = models.DateField(auto_now_add=True, verbose_name="Creado el ")
    update_at = models.DateField(auto_now = True, verbose_name = "Actualizado el")

    def save(self, *args, **kwargs):
        print(f"KWARGS {kwargs}")
        print("HOla")
        #Buscar los miembros que se encuentre en el proyecto que se esta guardando 
        member_in_proyect = get_list_or_404(Member,proyect__id=self.proyect.id)
        #Lista de id de los miembros obtenidos
        member_in_proyect_list = [(member.id) for member in member_in_proyect]
        
        if self.asigned_at.id not in member_in_proyect_list :
            raise ValueError("El usuario no pertenece al proyecto, la tarea no puede ser asignada")
        super().save(*args,**kwargs)
        
    def __str__(self):
        return f"{self.title } - {self.proyect}"
    
