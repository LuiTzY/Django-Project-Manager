from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm,TaskCreateForm,UpdateTaskForm,MemberRolForm,ProjectMembersForm, UpdateProjectForm
from .models import Proyect,Task,Member
from events.models import ProyectHistorial
from users.models import User
from django.contrib import messages
from datetime import datetime,timedelta
import random
import plotly.graph_objs as go
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.db.models.functions import TruncDate

def activity_chart(request):
    # Se obtienen las fechas y se cuentan el número de acciones por fecha desde la bd
    data = ProyectHistorial.objects.annotate(date=TruncDate('timestamp')).values('date').annotate(count=Count('id'))
    # Se extrae las fechas y las acciones para crear el gráfico
    dates = [entry['date'] for entry in data]
    counts = [entry['count'] for entry in data]
    
    # Se crea un grafico de actividad
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=counts,
                             mode='markers+lines', marker=dict(size=10),
                             name='Actividad de Proyecto'))
    fig.update_layout(title='Actividad de Proyecto',
                      xaxis_title='Fecha',
                      yaxis_title='Número de Acciones')

    # Convertir el grafico en formato JSON para renderizarlo en la plantilla de proyect-chart
    grafico_json = fig.to_json()

    # Se rendereiza la plantilla del grafico hecho con los datos obtenidos
    return render(request, 'proyects-chart.html', {'graph_json': grafico_json})

@login_required
def register_proyect(request):
    if request.method == "GET":
        return render(request, "proyect/create-proyect.html", {"form":ProjectForm()})
    else:
        projectForm = ProjectForm(data=request.POST)
        if projectForm.is_valid():
            
            Proyect.objects.create(
                project_name = projectForm.cleaned_data['project_name'],
                project_description = projectForm.cleaned_data['project_description'],
                proyect_objetive = projectForm.cleaned_data['proyect_objetive'],
                project_owner = request.user
            )
            ProyectHistorial.objects.create(action=f"Se ha creado el proyecto {projectForm.cleaned_data['project_name']} por {request.user.first_name}")
            messages.success(request,"Tu proyecto se ha creado correctamente")            
            return redirect("proyects")
        else:
            messages.error(request,"No se ha podido crear tu proyecto, intentalo de nuevo")
            return redirect("proyects")

@login_required
def getProyects(request):
    user = request.user  # Obtén el usuario actualmente autenticado
    proyectos_creados = Proyect.objects.filter(project_owner=user)
    
    """tareas_proyectos = {}  # Diccionario para almacenar las tareas de cada proyecto
    
    for proyecto in proyectos_creados:
        tareas_proyectos[proyecto] = proyecto.tareas.all()  # Obtén todas las tareas del proyecto actual
    
    print("Tareas de los proyectos: {}".format(tareas_proyectos))"""
    
    return render(request, "proyect/proyects.html", {"proyectos": proyectos_creados})

@login_required
def getProyect(request,project_id):
    user  = request.user
    proyect = Proyect.objects.get(project_owner=user, id=project_id)
    members = Member.objects.filter(proyect = proyect)
    members_names = [(member.user.first_name) for member in members]
    completed_tasks = Task.objects.filter(proyect = proyect, completed=True)
    ProyectHistorial.objects.create(action=f"{user} ha consultado el proyecto")
    return render(request, "proyect/proyect.html", {"proyect":proyect,"members":members,"tasks":proyect.tareas.all(),"completed_tasks":completed_tasks,"members_names":members_names})

@login_required
def updateProyect(request, project_id):
    proyect = Proyect.objects.get(id=project_id)
    queryset = Member.objects.filter(proyect =project_id, is_admin=True)
    admin_members = list(queryset)
    email_admin_members = [(member.user.email) for member in admin_members]
    email_admin_members.append(request.user.email)
    
    if request.method == "GET" and request.user.email in email_admin_members:
        return render(request, "proyect/edit-proyect.html",{"form":UpdateProjectForm})
    
    elif request.method == "POST" and request.user.email in email_admin_members:
        
        updateForm = UpdateProjectForm(instance=proyect,data=request.POST)
        if updateForm.is_valid():
            updateForm.save()
            ProyectHistorial.objects.create(action=f"{request.user.id} ha actualizado el proyecto {proyect.project_name}")
            messages.success(request,"El proyecto se ha actualizado correctamente")
            return redirect('proyect',project_id)
        else:
            ProyectHistorial.objects.create(action=f"{request.user.id} no pudo actualizar el proyecto")
            messages.error(request,"No se ha podido actualizar el proyecto correctamente")
            return redirect('proyect',project_id)
    else:
        messages.error(request,"No tienes permisos para editar este proyecto")
        ProyectHistorial.objects.create(action=f"{request.user.id} consulto el proyecto {proyect.project_name}, pero no posee permisos")
        return redirect('proyect',project_id)
    

@login_required
def createTask(request,project_id):
   proyect = Proyect.objects.get(id=project_id)
   if proyect is not None:
       if request.method == "GET":
            return render(request, "tasks/create-task.html", {"form":TaskCreateForm(instance=proyect)})
       else:
           task = TaskCreateForm(request.POST,instance=proyect)      
           if task.is_valid():
               #Se sacan los datos del form de cleaned_data
               task_asigned_at = task.cleaned_data['asigned_at'] 
               member = Member.objects.get(id=int(task_asigned_at))
               task_title = task.cleaned_data['title']
               task_description = task.cleaned_data['description'] 
               #Se crear una instacia para una tarea nueva, con los datos tomados del formulario enviado 
               Task.objects.create(asigned_at=member, proyect=proyect, title=task_title,description=task_description)
               ProyectHistorial.objects.create(action=f"{request.user.id} creo una tarea en el proyecto {proyect.project_name}")
               messages.success(request,"Se ha creado tu tarea correctamente")
               return redirect("tasks",project_id)
           else:
                ProyectHistorial.objects.create(action=f"{request.user.id} intento crear una tarea en el proyecto {proyect.project_name}, pero ocurrio un error")
                messages.error(request,"No se ha podido crear tu tarea, intentalo de nuevo")
                return redirect("create-task", project_id)
   else:
        return redirect('proyects')

@login_required
# todas las tareas
def all_tasks(request):
    user = User.objects.get(id=request.user.id)
    if user is not None:
        try:
            member = Member.objects.get(user__id=user.id)
            tasks = member.tareas_asignadas.all()
        except ObjectDoesNotExist:
            return render(request,"tasks/404.html")
        else:
            return render(request,"tasks/user-tasks.html", {"tasks":tasks})
       
            
@login_required
def getTask(request, task_id, project_id):
    proyect = Proyect.objects.get(id = project_id)
    members = Member.objects.filter(is_admin=True)
    admin_members = [(member.user.id) for member in members]
    task = Task.objects.get(proyect=proyect, id = task_id)
    if request.user.id in admin_members:
        ProyectHistorial.objects.create(action=f"{request.user.id} consulto la tarea {task.title} en el proyecto {proyect.project_name}")
        return render(request, "tasks/task.html", {"task":task,"admin_members":admin_members,"admin":True})
    else:
        ProyectHistorial.objects.create(action=f"{request.user.id} consulto la tarea {task.title} en el proyecto {proyect.project_name}")
        return render(request, "tasks/task.html", {"task":task,"admin_members":admin_members,"admin":False})
    
@login_required
def complete_task(request,task_id,project_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        task.completed = True
        task.datecompleted = timezone.now()
        task.save()
        ProyectHistorial.objects.create(action=f"{request.user.id} completo la tarea {task.title} en el proyecto {task.proyect.project_name}")
        messages.success(request,"La tarea ha sido completada correctamente")
        return redirect('task',task_id,project_id)
        
@login_required
def getTasks(request, project_id):
    proyect = Proyect.objects.get(id=project_id)
    if proyect is not None:
        tasks = proyect.tareas.all()
        if request.method == "GET":
            ProyectHistorial.objects.create(action=f"{request.user.id} consulto todas las tarea en el proyecto {proyect.project_name}")
            return render(request, "tasks/tasks.html", {"tasks":tasks, "proyect":proyect})
    else:
        messages.error(request,"El proyecto no existe")
        return redirect('profile')
        
@login_required
def editTask(request,task_id, project_id):
    proyect = Proyect.objects.get(id=project_id)
    task = Task.objects.get(id=task_id)
    if request.method == "GET":
        ProyectHistorial.objects.create(action=f"{request.user.id} solicito editar la tarea {task.title} en el proyecto {proyect.project_name}")
        return render(request, "edit-task.html",{"form":UpdateTaskForm(instance=task)})
    
    else:
        taskEditedForm = UpdateTaskForm(data=request.POST, instance=task)
        
        if taskEditedForm.is_valid():
            taskEditedForm.save()
            ProyectHistorial.objects.create(action=f"{request.user.id} edito la tarea {task.title} en el proyecto {proyect.project_name}")
            messages.success(request,f"Se ha editado tu tarea correctamente {task.title}")
            return redirect("tasks",project_id)
        else:
            ProyectHistorial.objects.create(action=f"{request.user.id} no pudo editar la tarea {task.title} en el proyecto {proyect.project_name}")
            messages.error(request,f"No se ha podido editar tu tarea {task.title} correctamente, intentalo de nuevo")
            return render("tasks",project_id)
        
@login_required        
def deleteTask(request, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()
    ProyectHistorial.objects.create(action=f"{request.user.id} elimino la tarea {task.title} en el proyecto {task.proyect.project_name}")
    messages.success(request, "Se ha eliminado la tarea correctamente")
    return redirect("proyects")

#Vista de roles 
@login_required
def change_member_role(request,project_id):
    proyect = Proyect.objects.get(id=project_id)
    project_members = proyect.project_members.all()
    ProyectHistorial.objects.create(action=f"{request.user.id} solicito cambiar los roles en el proyecto {proyect.project_name}")
    return render(request,'member-rol.html',{"form":MemberRolForm(),"members":project_members})

@login_required
def addProyectMember(request, project_id):
    proyect = Proyect.objects.get(id=project_id)
    if request.method == "GET":
        ProyectHistorial.objects.create(action=f"{request.user.id} solicito agregar miembros en el proyecto {proyect.project_name}")
        return render(request, "member/add-members.html", {"form":ProjectMembersForm(instance=proyect)})
    else:
        proyectMemberForm = ProjectMembersForm(request.POST, instance=proyect)

        if proyectMemberForm.is_valid():
            member_selected = proyectMemberForm.cleaned_data['user']
            member_rol = proyectMemberForm.cleaned_data['is_admin']
            member_rol_history = "Administrador" if member_rol else "Miembro"
            user_to_member = User.objects.get(id=member_selected)
            member_save = Member.objects.create(user=user_to_member, proyect=proyect, is_admin=member_rol)
            ProyectHistorial.objects.create(action=f"{request.user.id} agrego en el proyecto {proyect.project_name} al miembro {user_to_member.first_name} con el rol de :{member_rol_history}")

            messages.success(request,f"!El miembro {user_to_member.first_name} han sido agregados correctamente a tu proyecto !")
            return redirect("proyect-members",project_id=project_id)
        else:
            messages.error(request,f"No se ha podido agregar {user_to_member.first_name}")
            return render(request, "member/add-members.html", {"form":ProjectMembersForm(instance=proyect)})

@login_required
def listAllMembers(request, project_id):
    proyect = Proyect.objects.get(id=project_id)
    members = Member.objects.filter(proyect=project_id)
    admin_members =list(Member.objects.filter(proyect=project_id, is_admin=True))
    admin_members_list = [(member.user.id) for member in members]
    ProyectHistorial.objects.create(action=f"{request.user.id} listo todos los miembros del proyecto {proyect.project_name}")

    if request.user.id == proyect.project_owner.id:
        return render(request,"members.html",{"members":members,"proyect":proyect,"member_is_admin":False, "is_owner":True})

    if request.user.id in admin_members_list:
        return render(request,"members.html",{"members":members,"proyect":proyect,"member_is_admin":True, "is_owner":False})
    else:
        return render(request,"members.html",{"members":members,"proyect":proyect,"member_is_admin":False, "is_owner":False})

@login_required
def member_detail(request, project_id, member_id):
    #Miembro a mostrar informacion
    member = Member.objects.get(user_id = member_id, proyect_id = project_id)
    #Se obtienen todos los miembros para verificar roles
    members = Member.objects.filter(proyect=project_id)
    admin_members_list = [(member.user.id) for member in members]

    member_tasks = list(member.tareas_asignadas.all())
    member_tasks_title = [(task.title) for task in member_tasks]
    ProyectHistorial.objects.create(action=f"{request.user.id} solicito el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")

    #Si es creador del proyecto, puede eliminar 
    if request.user.id == member.proyect.project_owner.id:
        return render(request, "member/member-detail.html", {"member":member,"member_tasks":",".join(member_tasks_title), "is_owner":True})

    elif request.user.id in  admin_members_list:
        member_is_admin = False
        return render(request, "member/member-detail.html", {"member":member,"member_tasks":",".join(member_tasks_title),"member_is_admin":True})
    else:
        return render(request, "member/member-detail.html", {"member":member,"member_tasks":",".join(member_tasks_title),"member_is_admin":False})


    """  activity_data = {
            '2022-01-01': 10,
            '2022-01-02': 15,
            '2022-01-03': 20,
            # Agrega más datos aquí
        }

        # Procesar los datos para crear el gráfico
    labels = list(activity_data.keys())
    values = list(activity_data.values())

        # Crear el gráfico con Plotly
    trace = go.Scatter(x=labels, y=values, mode='lines+markers')
    layout = go.Layout(title='Gráfico de Actividad', xaxis=dict(title='Fecha'), yaxis=dict(title='Actividad'))
    fig = go.Figure(data=[trace], layout=layout)
    plot_div = fig.to_html(full_html=False)"""
    

@login_required
def member_change_rol(request, project_id, member_id):
    member = Member.objects.get(user_id = member_id, proyect_id = project_id)
    
    if member.is_admin:
        member.is_admin = False
        member.save()
        messages.success(request,f"El miembro {member.user.first_name} del proyecto {member.proyect.project_name} es Administrador del proyecto")
    else:
        member.is_admin = True
        member.save()
        messages.success(request,f"El miembro {member.user.first_name} del proyecto {member.proyect.project_name} es Miembro del proyecto")
        
    ProyectHistorial.objects.create(action=f"{request.user.id} cambio el rol del miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
    return redirect("member-detail", project_id ,member_id)


@login_required
def delete_member(request, project_id, member_id):
    member = Member.objects.get(user_id = member_id, proyect_id = project_id)
    member_name = member.user.first_name
    if member is not None:
        member.delete()
        messages.success(f"Se ha eliminado correctamente el miembro {member_name} de tu proyecto")
        ProyectHistorial.objects.create(action=f"{request.user.id} solicito eliminar el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
        ProyectHistorial.objects.create(action=f"{request.user.id} elimino el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
        return redirect("proyect-members",project_id)

    ProyectHistorial.objects.create(action=f"{request.user.id} fallo en eliminar el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
    messages.error(f"No se ha podido eliminar el miembro {member.user.first_name} de tu proyecto, intentalo mas tarde")
    return redirect("proyects-members", project_id)