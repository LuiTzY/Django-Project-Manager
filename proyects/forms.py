from django import forms # type: ignore
from .models import Proyect,Task,Member,User

#Formulario para crear un proyecto
class ProjectForm(forms.ModelForm):
    #cuando el form se valla a guardar, se llama al modelo para guardar estos datos
    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
    #modelo con el que el formulario esta relacionado
    class Meta:
        model = Proyect
        fields = ("project_name","project_description","proyect_objetive")
        widgets = {
            #atributos y clases de los campos del form
            'project_name' :forms.TextInput(attrs={
                'class':'form-control',
                'minlength':'6',
                
            }),
            'project_description': forms.Textarea(attrs={
                'class':'form-control'
            }),
            'proyect_objetive':forms.TextInput(attrs={
                'class':'form-control'
            })
        }
#form para actualizar un proyecto
class UpdateProjectForm(forms.ModelForm):
    #modelo al que estara relacionado el form
    class Meta:
        model = Proyect
        fields = ("project_name","project_description","proyect_objetive")
        widgets = {
            #atributos y clases del formulario
            'project_name' :forms.TextInput(attrs={
                'class':'form-control',
                'minlength':'6',
                'placeholder':"Escribe el nuevo nombre de tu proyecto"
                
            }),
            'project_description': forms.Textarea(attrs={
                'class':'form-control',
                'placeholder':'Escribe una nueva descripcion'
            }),
            'proyect_objetive':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Escribe el nuevo objetivo'
            })
        }
#formulario para miembros del proyecto
class ProjectMembersForm(forms.ModelForm):
    #cuando se inice el form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #si hay una instancia, para determinar a que proyecto se le agregar x miembro
        if 'instance' in kwargs:
            proyect_owner = kwargs['instance'].project_owner
            #Va a buscar en la instancia pasada del proyecto, el id del proyecto para filtrar los miembros que tengan el id
            #del proyecto al que se le quieren agregar los miembros
            excluded_users = list(Member.objects.filter(proyect=kwargs['instance'].id).values_list('user_id', flat=True))
            print(excluded_users)
            
            members_in_proyect = list(Member.objects.filter(proyect=kwargs['instance'].id).values_list('user_id', flat=True))
            
            excluded_users = [user_id for user_id in excluded_users if user_id  in members_in_proyect]
            
            users = User.objects.exclude(id__in=excluded_users)
            self.fields['user'].choices = [(user.id, user.first_name) for user in users]
    user = forms.TypedChoiceField(
        choices=[],  
        required=False,
        label="Miembros disponibles",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    #modelo al que esta relacionado el formulario
    class Meta:
        model = Member
        #campos que se usaran del modelo
        fields = ('user','is_admin')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }
      
        

class TaskCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        #se llama al constructor del modelo relacionado 
        super().__init__(*args, **kwargs)
        # Verifico si se ha pasado una instancia como argumento
        if 'instance' in kwargs:
            proyect_id = kwargs['instance'].id
            # Filtro los miembros disponibles para ese proyecto
            members_proyect_available = Member.objects.filter(proyect__id=proyect_id)
            list(members_proyect_available)
            # Si hay miembros disponibles
            if members_proyect_available is not None:
                self.fields['asigned_at'].choices = [(member.id, member.user.first_name) for member in members_proyect_available]
                
    def save(self, *args, **kwargs):
     
            super().save(*args, **kwargs)
            
    asigned_at = forms.TypedChoiceField(
        choices=[],
        required=False,
        label="La tarea sera asignada a:"
    )
    #modelo al que pertenece el formulario
    class Meta:
        model = Task
        fields = ("title","description","asigned_at")
        widgets = {
            #clases y atributos de los formularios
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción', 'rows': 3}),
            'asigned_at': forms.Select(attrs={'class': 'form-control'})
        }

class UpdateTaskForm(forms.ModelForm):
    #cuando se inicie el form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #si hay una instancia, donde se llame el form, obtenemos los datos 
        if 'instance' in kwargs:
            #se obtiene el id del proyecto de la instancia pasada que seria (proyect)
            proyect_id = kwargs['instance'].proyect.id
            #se filtra por los mimebros disponibles en el proyecto para actualizar una tarea
            members_proyect_available = Member.objects.filter(proyect__id=proyect_id)
            #se convierte en una lista
            list(members_proyect_available)
            # si hay miembros
            if members_proyect_available is not None:
                #se les asigna al cmapo las opciones de los miembros
                self.fields['asigned_at'].choices = [(member.id, member.user.first_name) for member in members_proyect_available]
                
    def clean_asigned_at(self):
        asigned_at_id = self.cleaned_data.get('asigned_at')
        try:
            #se otbiene el miebro
            member = Member.objects.get(id=asigned_at_id)
            return member
        except Member.DoesNotExist:
            #el miembro que se eligio no existe
            raise forms.ValidationError("No se puede asignar la tarea a un miembro inexistente.")
    #se llama el metodo para guardar el form
    def save(self, *args, **kwargs):
  
            super().save(*args, **kwargs)
    #las opciones a los que se les asignara una tarea
    asigned_at = forms.TypedChoiceField(
        choices=[],
        required=False,
        label="La tarea sera asignada a:"
    )
    class Meta:
        #se especifica al modelo que pertenece el formulario
        model = Task
        #campos que se usaran del modelo
        fields = ("title","description","asigned_at")
        widgets = {
            #clases y atributos a los formularios
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción', 'rows': 3}),
            'asigned_at': forms.Select(attrs={'class': 'form-control'})
        }
#formulario para completar una tarea
class CompleTask(forms.ModelForm):
    #se especifica al modelo que pertenece el formulario
    class Meta:
        #campos que se usaran del modelo
        fields = ("completed",)
        widgets = {
            'completed': forms.BooleanField()
        }
# formulario para el rol de un miembro
class MemberRolForm(forms.ModelForm):
    #se especifica al modelo que pertenece el formulario
   class Meta:
       model = Member
        #campos que se usaran del modelo  
       fields = ("is_admin",)