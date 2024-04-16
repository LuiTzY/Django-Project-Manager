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

#vista para ver las acciones relacionas con todos los proyectos
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
    return render(request, 'proyect/proyects-chart.html', {'graph_json': grafico_json})

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para crear un proyecto
def register_proyect(request):
    #si la solicitud es por get, se renderiza la plantilla con el formulario para crear un proyecto
    if request.method == "GET":
        return render(request, "proyect/create-proyect.html", {"form":ProjectForm()})
    else:
        """
            Los datos son enviados por post, se intancia el formulario con los
            datos recibidos del proyecto, para verificar si estos son validos o no
            de acuerdo al modelo relacionado
        """
        projectForm = ProjectForm(data=request.POST)
        #Si el formulario es valido
        if projectForm.is_valid():
            """
                Se crea una instancia de un proyecto, con los datos validados guardaos en cleaned_data
            """
            Proyect.objects.create(
                project_name = projectForm.cleaned_data['project_name'],
                project_description = projectForm.cleaned_data['project_description'],
                proyect_objetive = projectForm.cleaned_data['proyect_objetive'],
                project_owner = request.user
            )
            #se registra la accion realizada 
            ProyectHistorial.objects.create(action=f"Se ha creado el proyecto {projectForm.cleaned_data['project_name']} por {request.user.first_name}")
            #se crea un mensaje del proyecto
            messages.success(request,"Tu proyecto se ha creado correctamente")  
            #se redirecciona a todos los proyectos de el usuario          
            return redirect("proyects")
        #el formulario no es valido
        else:
            #se crea un mensaje de error
            messages.error(request,"No se ha podido crear tu proyecto, intentalo de nuevo")
            #se redirecciona a los proyectos
            return redirect("proyects")

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para obtener los proyectos del usuario
def getProyects(request):
    #proyectos creados por el usuarios
    proyectos_creados = Proyect.objects.filter(project_owner=request.user)  
    #se renderiza la plantilla de los proyectos del usuario  
    return render(request, "proyect/proyects.html", {"proyectos": proyectos_creados})

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
def proyects_member(request):
    members_proyect = Member.objects.filter(user__id= request.user.id)
    return render(request, "member/proyects-member.html", {"members_proyect": members_proyect})

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para obtener el id del proyecto
def getProyect(request,project_id):
    try:
        """
            Se busca el proyecto que coincida con el id del proyecto solicitado y
            se extrae la informacion de este, se buscan los miembros de proyecto
            y las tareas que han sido completadas
        """
        proyect = Proyect.objects.get(project_owner=request.user, id=project_id)
        members = Member.objects.filter(proyect = proyect)
        members_names = [(member.user.first_name) for member in members]
        completed_tasks = Task.objects.filter(proyect = proyect, completed=True)
    except ObjectDoesNotExist:
        #si no existe se crea un mensaje de error y se redirecciona a un 404
        return render(request,"proyect/404-proyect.html")
    # se registra la accion realizada  y se renderiza el proyecto obtenido con los miembros, el proyecto y las tareas
    ProyectHistorial.objects.create(action=f"{request.user} ha consultado el proyecto")
    return render(request, "proyect/proyect.html", {"proyect":proyect,"members":members,"tasks":proyect.tareas.all(),"completed_tasks":completed_tasks,"members_names":members_names})

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para actualizar un proyecto, (parametros)= id del proyecto
def updateProyect(request, project_id):
    try:
        #se busca el proyecto que coincida con el id proporcionado
        proyect = Proyect.objects.get(id=project_id)
        #se filtran los miembros del proyectos que tengan el rol de administrador
        queryset = Member.objects.filter(proyect =project_id, is_admin=True)
        
    except ObjectDoesNotExist:
        #si el proyecto no existe, se renderiza un 404 
        return render(request,"proyect/404-proyect.html")
    
    #se convierte en lista los miembros administradores
    admin_members = list(queryset)
    #se crea una nueva lista que almacene los correos de los miembros administradores
    email_admin_members = [(member.user.email) for member in admin_members]
    #se agrega el correo del usuario 
    email_admin_members.append(request.user.email)
    
    #si la solicitud es por get y el email del usuario que la hace esta dentro de los miembros administradores, podra ver el formulario para actualizar el proyecto
    if request.method == "GET" and request.user.email in email_admin_members:
        return render(request, "proyect/edit-proyect.html",{"form":UpdateProjectForm})
    
    #Si se envia el formulario y el email del usuario que la hace tiene los roles adecuados, lo podra guardar
    elif request.method == "POST" and request.user.email in email_admin_members:
        #se instancia los datos llegados por el post en el modelo del formulario, con la instancia del proyecto
        updateForm = UpdateProjectForm(instance=proyect,data=request.POST)
        #si es valido
        if updateForm.is_valid():
            #se guardan los datos, las acciones realizadas, un mensaje de exito y se redirecciona al proyecto actualizado
            updateForm.save()
            ProyectHistorial.objects.create(action=f"{request.user.id} ha actualizado el proyecto {proyect.project_name}")
            messages.success(request,"El proyecto se ha actualizado correctamente")
            return redirect('proyect',project_id)
        #no es valido
        else:
            #se crea un mensaje de la accion realizada, un mensaje de error y la vista del proyecto consultado
            ProyectHistorial.objects.create(action=f"{request.user.id} no pudo actualizar el proyecto")
            messages.error(request,"No se ha podido actualizar el proyecto correctamente")
            return redirect('proyect',project_id)
    #el usuario no esta dentro de la lista de administrados, lo que quiere decir que no tiene permisos para actualizar un proyecto
    else:
        #se crea mensaje de error, registra accion realizada y se redirecciona al proyecto
        messages.error(request,"No tienes permisos para editar este proyecto")
        ProyectHistorial.objects.create(action=f"{request.user.id} consulto el proyecto {proyect.project_name}, pero no posee permisos")
        return redirect('proyect',project_id)
    
@login_required
def delete_proyect(request, project_id):
    try:
        proyect = Proyect.objects.get(id=project_id)
        proyect.delete()
    except ObjectDoesNotExist:
        return render(request,"proyect/404-proyect.html")
    else:
        messages.success(request,"El proyecto se elimino correctamente")
        return redirect("proyects")

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para crear una tarea, (parametros) = id del proyecto
def createTask(request,project_id):
   try: 
       # se busca el proyecto que coincida con ese id
    proyect = Proyect.objects.get(id=project_id)
    #se obtienen los miembros a los que las tareas seran asignadas que coincidad con el id del proyecto
    members = Member.objects.filter(proyect=proyect)
   except ObjectDoesNotExist:
       #el proeycto no existe, 404 
        return render(request,"proyect/404-proyect.html")
    
    #si el proyecto no es None, es decir si existe
   if proyect is not None:
       #si la solicitud es por get, se renderiza el formulario para crear la tarea
       if request.method == "GET":
            return render(request, "tasks/create-task.html", {"form":TaskCreateForm(instance=proyect),"proyect":proyect,"members":members})
       else:
           #se obtiene los datos que llegan por el post, instanciadolos al formulario para crear la tarea
           task = TaskCreateForm(request.POST,instance=proyect) 
           #si es valida     
           if task.is_valid():
               #Se sacan los datos del form de cleaned_data
               task_asigned_at = task.cleaned_data['asigned_at'] 
               member = Member.objects.get(id=int(task_asigned_at))
               task_title = task.cleaned_data['title']
               task_description = task.cleaned_data['description'] 
               #Se crear una instacia para una tarea nueva, con los datos tomados del formulario enviado 
               Task.objects.create(asigned_at=member, proyect=proyect, title=task_title,description=task_description)
               ProyectHistorial.objects.create(action=f"{request.user.id} creo una tarea en el proyecto {proyect.project_name}")
               #se crea un mensaje de exito
               messages.success(request,"Se ha creado tu tarea correctamente")
               #redireccion a todas las tareas que coincidan con el id del proyecto
               return redirect("tasks",project_id)
           #no es valido
           else:
               #se registra la accionr realizada
                ProyectHistorial.objects.create(action=f"{request.user.id} intento crear una tarea en el proyecto {proyect.project_name}, pero ocurrio un error")
                #se crea un mensaje de error
                messages.error(request,"No se ha podido crear tu tarea, intentalo de nuevo")
                #se redirecciona al formulario para crear la tarea coon el id del proyecto
                return redirect("create-task", project_id)
   else:
       #se redireccionan a los proyectos
        return redirect('proyects')

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
# vista para ver todas las tareas del usuario, no tiene parametros
def all_tasks(request):
    
    user = User.objects.get(id=request.user.id)
    if user is not None:
        #si es un usuario
        try:
            #se obtienen los miembros para obtener todos los proyectos a los que el usuario es miembro 
            member = Member.objects.get(user__id=user.id)
            #se obtiene todas estas tareas
            tasks = member.tareas_asignadas.all()
        except ObjectDoesNotExist:
            #no existen tareas asociados a un miembro con el usuario
            return render(request,"tasks/404.html")
        else:
            #se redirecciona a los tareas del usario
            return render(request,"tasks/user-tasks.html", {"tasks":tasks})
       
            
@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para obtener una tarea, (parametros) = id de la tarea y del proyecto
def getTask(request, task_id, project_id):
    try:
        #se obtiene el proyecto que coincida con ese id
        proyect = Proyect.objects.get(id = project_id)
    except ObjectDoesNotExist:
        #no existe el proyecto
        return render(request,"proyect/404-proyect.html")
    
    #se obtiene los miembros que son administradores
    members = Member.objects.filter(is_admin=True)
    #se convierte en una lista con los ids de los proyectos que coincidan con esos proyectos
    admin_members = [(member.user.id) for member in members]
    try:
        #se obtiene la tarea
        task = Task.objects.get(proyect=proyect, id = task_id)
    except ObjectDoesNotExist:
        #la tarea no existe
        return render(request,"tasks/404-tasks.html")
    #si el usuario que hace la solicitud esta dentro de los miembros administradores
    if request.user.id in admin_members:
        # se registra el evento con la accion relacionada
        ProyectHistorial.objects.create(action=f"{request.user.id} consulto la tarea {task.title} en el proyecto {proyect.project_name}")
        #se redirecciona a la vista de las tareas
        return render(request, "tasks/task.html", {"task":task,"admin_members":admin_members,"admin":True})
    else:
        #se registra el evento con la accion y se redirecciona a las tareas de ese proyecto
        ProyectHistorial.objects.create(action=f"{request.user.id} consulto la tarea {task.title} en el proyecto {proyect.project_name}")
        return render(request, "tasks/task.html", {"task":task,"admin_members":admin_members,"admin":False})
    
@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para completar la tarea, (parametros) = id de la tarea y id del proyecto
def complete_task(request,task_id,project_id):
    #se obtiene la taraa
    task = Task.objects.get(id=task_id)
    #si es por post la solicutd
    if request.method == "POST":
        #se actualiza la tarea, con la fecha en la que se actualizo y su estado de completa en True
        task.completed = True
        task.datecompleted = timezone.now()
        task.save()
        #se regista el evento con la accion relacionada , mensaje de exito y se redirecciona a las tareas
        ProyectHistorial.objects.create(action=f"{request.user.id} completo la tarea {task.title} en el proyecto {task.proyect.project_name}")
        messages.success(request,"La tarea ha sido completada correctamente")
        return redirect('task',task_id,project_id)
        
@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para obtener las tareas, (parametros)=  id del proyecto
def getTasks(request, project_id):
    try:
        # se obtienen el proyecto y los miembros para ver sus tareas
        proyect = Proyect.objects.get(id=project_id)
        members = Member.objects.filter(proyect=proyect)
    except ObjectDoesNotExist:
        #no existe el proyecto
        return render(request,"proyect/404-proyect.html")
    if proyect is not None:
        #si es un proyecto valido, se obtiene todas las tarea
        tasks = proyect.tareas.all()
        # si es por get
        if request.method == "GET":
            #se renderizan las tareas
            ProyectHistorial.objects.create(action=f"{request.user.id} consulto todas las tarea en el proyecto {proyect.project_name}")
            return render(request, "tasks/tasks.html", {"tasks":tasks, "proyect":proyect, "members":members})
    else:
        messages.error(request,"El proyecto no existe")
        return redirect('profile')
        
@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para editar las tareas, (parametros)=id de la tarea y del proyecto
def editTask(request,task_id, project_id):
    try:
        #se obtiene el proyecto
        proyect = Proyect.objects.get(id=project_id)
    except ObjectDoesNotExist:
        # el proyecto no existe
        return render(request,"proyect/404-proyect.html")
    try:
        #se obtiene la taraa
        task = Task.objects.get(id=task_id)
    except ObjectDoesNotExist:
        #no existe la tarea que conicida con el id
        return render(request,"tasks/404-tasks.html")
    
    if request.method == "GET":
        #se registra un evento con la accion realizada
        ProyectHistorial.objects.create(action=f"{request.user.id} solicito editar la tarea {task.title} en el proyecto {proyect.project_name}")
        #se redirecciona al formulario de actualizar una tarea, con la instancia de la tarea, para asi ver los datos de la tarea a editar
        return render(request, "tasks/edit-task.html",{"form":UpdateTaskForm(instance=task)})
    
    else:
        taskEditedForm = UpdateTaskForm(data=request.POST, instance=task)
        #es valido
        if taskEditedForm.is_valid():
            #se guarda la tarea editada
            taskEditedForm.save()
            #se registra el evento con la accion realizada, un mensaje de exito y las tareas
            ProyectHistorial.objects.create(action=f"{request.user.id} edito la tarea {task.title} en el proyecto {proyect.project_name}")
            messages.success(request,f"Se ha editado tu tarea correctamente {task.title}")
            return redirect("tasks",project_id)
        #no es valido
        else:
            #Se registra el evento con la accion realizada, un mensaje de error y de se renderiza las tareas que coincidad con el id del proyecto
            ProyectHistorial.objects.create(action=f"{request.user.id} no pudo editar la tarea {task.title} en el proyecto {proyect.project_name}")
            messages.error(request,f"No se ha podido editar tu tarea {task.title} correctamente, intentalo de nuevo")
            return render("tasks",project_id)
        
@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login  
#vista para eliminar una tarea, (parametros)= id de la tarea, no ncesitamos el id del proyecto ya que la tarea es unica y en el objeto de la tarea esta viene con el proyecto incluido      
def deleteTask(request, task_id):
    try:
        #se obtiene la tarea
        task = Task.objects.get(id=task_id)
        #se borra si es obtenida
        task.delete()
    except ObjectDoesNotExist:
        # no hay tarea que coincida con el id proporcionado, no existe
        return render(request,"tasks/404-tasks.html")
    
    #Se registra el evento con la accion realizada, se crea un mensaje de exito y se redirecciona a los proeyctos del usuario
    ProyectHistorial.objects.create(action=f"{request.user.id} elimino la tarea {task.title} en el proyecto {task.proyect.project_name}")
    messages.success(request, "Se ha eliminado la tarea correctamente")
    return redirect("proyects")

#Vista de roles 
@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
def change_member_role(request,project_id):
    try:
        #Se obtiene el proyecto por el id proporcionado
        proyect = Proyect.objects.get(id=project_id)
        #obtener todos los miembros del proyecto
        project_members = proyect.project_members.all()
    except ObjectDoesNotExist:
        #El id del proyecto no existe, se redirecciona a un 404 
        return render(request,"proyect/404-proyect.html")
    #Se registra la accion realizada del proyecto 
    ProyectHistorial.objects.create(action=f"{request.user.id} solicito cambiar los roles en el proyecto {proyect.project_name}")
    #Se renderiza el formulario para cambiar el rol de un miembro
    return render(request,'member/member-rol.html',{"form":MemberRolForm(),"members":project_members})

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para agregar un miembro a un proyecto, (parametros) = id del proyecto
def addProyectMember(request, project_id):
    
    try:
        #se intenta obtener el proyecto
        proyect = Proyect.objects.get(id=project_id)
    except ObjectDoesNotExist:
        #el id del proyecto es invalido, lo que quiere decir que no existe, se renderiza la plantilla de 404 
        return render(request,"proyect/404-proyect.html")
    
    #Si la solicitud es por get, el formulario se va a renderizar 
    if request.method == "GET":
        #Se crea un evento con la accion realizada
        ProyectHistorial.objects.create(action=f"{request.user.id} solicito agregar miembros en el proyecto {proyect.project_name}")
        
        #Se renderiza el formulario para agregar un miembro al proyecto, con la instancia del proyecto obtenido
        return render(request, "member/add-members.html", {"form":ProjectMembersForm(instance=proyect)})
    
    else:
        
        """
            Si esto se activa, es porque el formulario fue enviado,
            instanciamos el formulario con los datos que nos envian
            por el post, con la instancia del proyecto para saber que proyecto
            es el que se le realizaran los cambios, al los datos ser pasado
            el formulario lanzara errores si los datos no son correctos a los del
            modelo asociado al formulario
        """
        
        proyectMemberForm = ProjectMembersForm(request.POST, instance=proyect)
        #Si al hacer enviar el formulario, los datos son validos
        if proyectMemberForm.is_valid():
            
            """
                Se obtienes los datos del formulario para crear una instancia de el miembro a 
                guardar, estos datos son guardados en un diccionario cleaned_data al ser validos
            """
            member_selected = proyectMemberForm.cleaned_data['user']
            member_rol = proyectMemberForm.cleaned_data['is_admin']
            
            #se guarda el rol del miembro, para guardar la accion del rol que se le asigno
            member_rol_history = "Administrador" if member_rol else "Miembro"
            
            #hacemos una consulta para obtener informacion del miembro creado
            user_to_member = User.objects.get(id=member_selected)
            
            #Creamos el miembro, con los datos requeridos en el modelo
            Member.objects.create(user=user_to_member, proyect=proyect, is_admin=member_rol)
            #Se crea un evento registrando la accion realizada

            ProyectHistorial.objects.create(action=f"{request.user.id} agrego en el proyecto {proyect.project_name} al miembro {user_to_member.first_name} con el rol de :{member_rol_history}")
            #Se crea mensaje de exito

            messages.success(request,f"!El miembro {user_to_member.first_name} han sido agregados correctamente a tu proyecto !")
            #se redirecciona a los miembros del proyecto (parametros) = id del proyecto

            return redirect("proyect-members",project_id=project_id)
        #Si el formulario no es valido
        else:
            #Se crea un mensaje de error
            messages.error(request,f"No se ha podido agregar {user_to_member.first_name}")
            #Se renderiza la plantila, con el formulario nuevamente, con la instacia del proyecto, para saber cual es el proyecto a actualizar
            return render(request, "member/add-members.html", {"form":ProjectMembersForm(instance=proyect)})
        

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para listar todos los miembros de un proyecto, (parametros) = id del proyecto
def listAllMembers(request, project_id):
    try:
        #Se busca el proyecto que coincida con el id solicitado
        proyect = Proyect.objects.get(id=project_id)
        #Se buscan los miembros de ese proyecto
        members = Member.objects.filter(proyect=project_id)

    except ObjectDoesNotExist:
        #El proyecto no existe
        return render(request,"proyect/404-proyect.html")
    
    #Lista de los miembros administradores del proyecto
    admin_members =list(Member.objects.filter(proyect=project_id, is_admin=True))
    
    #Lista de los id de los miembros administradores
    admin_members_list = [(member.user.id) for member in members]
    #Se crea un evento, registrando la accion hecha del proyecto
    ProyectHistorial.objects.create(action=f"{request.user.id} listo todos los miembros del proyecto {proyect.project_name}")

    if request.user.id == proyect.project_owner.id:
        #se renderiza los miembros solicitado del proyecto, el proyecto y el rol del usuario que esta haciendo la solicitud 
        return render(request,"member/members.html",{"members":members,"proyect":proyect,"member_is_admin":False, "is_owner":True})

    if request.user.id in admin_members_list:
        #se renderiza los miembros solicitado del proyecto, el proyecto y el rol del usuario que esta haciendo la solicitud 
        return render(request,"member/members.html",{"members":members,"proyect":proyect,"member_is_admin":True, "is_owner":False})
    else:
        #se renderiza los miembros solicitado del proyecto, el proyecto y el rol del usuario que esta haciendo la solicitud 
        return render(request,"member/members.html",{"members":members,"proyect":proyect,"member_is_admin":False, "is_owner":False})

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login
#vista para obtener el detalle de un miembro (parametros) = id del proyecto, id del miembro
def member_detail(request, project_id, member_id):
    """
        Esta vista require verificar si el proyecto existe primero, si no redirecciona a un 404, luego si realmente
        existe se verifica si el miembro pertenece a ese proyecto, si no pertenece redirecciona a un 404, si los 2
        son validos se renderiza los detalles del miembro
    """
    
    try:
        #se intenta obtener el proyecto
        proyect = Proyect.objects.get(id=project_id)
        
    except ObjectDoesNotExist:
        #si el proyecto no existe se redirecciona a un 404 de que no existe el proyecto
        return render(request,"proyect/404-proyect.html")    
    #Miembro a mostrar informacion
    try:
        #se intenta obtener el miembro 
        member = Member.objects.get(user_id = member_id, proyect_id = project_id)
        
    except ObjectDoesNotExist:
        #si no existe, se redirecciona a un 404 de que no existe 
        return render(request, "member/404-members.html",{"message":"Lo sentimos, pero este miembro no existe en tu proyecto","proyect":proyect})
    
    #Se obtienen todos los miembros para verificar los roles
    members = Member.objects.filter(proyect=project_id)
    
    #Se crea una lista que contiene los id de los miembros obtenidos del proyecto
    admin_members_list = [(member.user.id) for member in members]
    
    #Se crea una lista de las tareas de el miembro consultado 
    member_tasks = list(member.tareas_asignadas.all())
    #se guarda en la lista, los titulos de las tareas obtenidas
    member_tasks_title = [(task.title) for task in member_tasks]
    #se crea un evento del proyecto, para guardar la accion
    ProyectHistorial.objects.create(action=f"{request.user.id} solicito el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")

    #Si el usuario en la request es el creador del proyecto, puede eliminar
    if request.user.id == member.proyect.project_owner.id:
        #se renderiza una vista, con el miembro solicitado, las tareas del miembro y su rol
        return render(request, "member/member-detail.html", {"member":member,"member_tasks":",".join(member_tasks_title), "is_owner":True})
    #Si el usuario en la request esta en la lista de los miembros 
    elif request.user.id in admin_members_list:
        #se renderiza una vista, con el miembro solicitado, las tareas del miembro y su rol
        return render(request, "member/member-detail.html", {"member":member,"member_tasks":",".join(member_tasks_title),"member_is_admin":True})
    else:
        #se renderiza una vista, con el miembro solicitado, las tareas del miembro y su rol
        return render(request, "member/member-detail.html", {"member":member,"member_tasks":",".join(member_tasks_title),"member_is_admin":False})

@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login

#vista para cambiar el rol de un miembro (parametros) = id del proyecto, id del miembro
def member_change_rol(request, project_id, member_id):
    #se intenta obtener el miembro solicitado
    try:
        member = Member.objects.get(user_id = member_id, proyect_id = project_id)
        
    except ObjectDoesNotExist:
        #Si el miembro no existe, se redirecciona a un 404 de los miembros
        return render(request, "member/404-members.html",{"message":"Lo sentimos, pero este miembro no existe en tu proyecto"})
    
    # si el miembro es administrador
    if member.is_admin:        
        #su rol cambiara a un miembro regular
        member.is_admin = False
        #se actualiza su rol
        member.save()
        # se crea mensaje de exito al ser actualizado correctamente el rol
        messages.success(request,f"El miembro {member.user.first_name} del proyecto {member.proyect.project_name} es Administrador del proyecto")
    #caso contrario
    else:
         #su rol cambiara a un administrador del proyecto
        member.is_admin = True
        #se actualiza su rol
        member.save()
        # se crea mensaje de exito al ser actualizado correctamente el rol
        messages.success(request,f"El miembro {member.user.first_name} del proyecto {member.proyect.project_name} es Miembro del proyecto")
    
    #Se captura el evento de que se cambio un rol de un miembro
    ProyectHistorial.objects.create(action=f"{request.user.id} cambio el rol del miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
    
    #se redirecciona a los detalles del miembro enviando los parametros del proyecto y el id del miembro
    return redirect("member-detail", project_id ,member_id)


@login_required #vista protegida, cuando se haga una solicitud y no este autenticado, lo redirecciona al login

#vista para borrar un miembro, (parametros) = id del proyecto, id del miembro
def delete_member(request, project_id, member_id):
    #Intetamos obtener el miembro por su id
    try:
        member = Member.objects.get(user_id = member_id, proyect_id = project_id)
        #Sacamos el nombre del miembro del objeto obtenido de la consulta
        member_name = member.user.first_name
    except ObjectDoesNotExist:
        
        #Si el mimebro no existe, se crea una instancia para capturar el evento de que no se pudo eliminar el meimbro
        ProyectHistorial.objects.create(action=f"{request.user.id} fallo en eliminar el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
        #creamos un menasje de error
        messages.error(f"No se ha podido eliminar el miembro {member.user.first_name} de tu proyecto, intentalo mas tarde")
        #redireccion a una vista de 404 al el miembro no ser encontrado
        return render(request, "member/404-members.html",{"message":"Lo sentimos, pero este miembro no existe en tu proyecto"})
       
    if member is not None:
        #si el miembro no es None, lo borramos
        member.delete()
        #Se crea un mensaje de exito al haber eliminado el miembro del proyecot
        messages.success(request,f"Se ha eliminado correctamente el miembro {member_name} de tu proyecto")
        #Creamos 2 instancias de ProyectHistorial para capturar los eventos hechos
        ProyectHistorial.objects.create(action=f"{request.user.id} solicito eliminar el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
        ProyectHistorial.objects.create(action=f"{request.user.id} elimino el miembro {member.user.first_name} del proyecto {member.proyect.project_name}")
        #Redireccionamos a la vista de los mimembros del proyecto junto con el parametro del id del proyecto
        return redirect("proyect-members",project_id)

    
