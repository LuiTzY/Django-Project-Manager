from django.urls import path
from . import views

#Rutas de los proyectos,tareas y miembros para realizar las acciones
urlpatterns = [
    path('create-proyect/', views.register_proyect, name="create-proyect"),
    path('proyects/', views.getProyects, name="proyects"),
    path('proyects-member/', views.proyects_member, name="proyects-member"),
    path('proyect/<project_id>/', views.getProyect, name="proyect"),
    path('update-proyect/<project_id>/', views.updateProyect, name="edit-proyect"),
    
    path('create-task/<project_id>/', views.createTask, name="create-task"),
    path('task/<task_id>/<project_id>', views.getTask, name="task"),
    path('all-tasks/', views.all_tasks, name="all-tasks"),
    path('tasks/<project_id>/', views.getTasks, name="tasks"),
    path('edit-task/<int:task_id>/<int:project_id>/', views.editTask, name="edit-task"),
    path('complete-task/<task_id>/<project_id>/', views.complete_task, name="complete-task"),
    path('delete-task/<int:task_id>', views.deleteTask, name="delete-task"),
    
    path('edit-member-rols/<project_id>/', views.change_member_role, name="edit-members-rols"),
    path('add-member/<project_id>/', views.addProyectMember, name="add-member"),
    path('list-members/<project_id>/', views.listAllMembers, name="proyect-members"),
    path('member-detail/<project_id>/<member_id>/', views.member_detail, name="member-detail"),
    path('member-change-rol/<project_id>/<member_id>/', views.member_change_rol, name="update-member-rol"),
    path('delete-member/<project_id>/<member_id>/', views.delete_member, name="delete-member"),
    path('proyects-charts-activity/',views.activity_chart, name="graphic")
]