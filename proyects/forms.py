from django import forms
from .models import Proyect,Task,Member,User

class ProjectForm(forms.ModelForm):
    def save(self, *args, **kwargs):
            print("SE INTENTA GUARDAR PORYECTO")
            super().save(*args, **kwargs)
    class Meta:
        model = Proyect
        fields = ("project_name","project_description","proyect_objetive")
        widgets = {
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
        
class UpdateProjectForm(forms.ModelForm):
    class Meta:
        model = Proyect
        fields = ("project_name","project_description","proyect_objetive")
        widgets = {
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

class ProjectMembersForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            proyect_owner = kwargs['instance'].project_owner
            #Va a buscar en la instancia pasada del proyecto, el id del proyecto para filtrar los miembros que tengan el id
            #del proyecto al que se le quieren agregar los miembros
            excluded_users = list(Member.objects.filter(proyect=kwargs['instance'].id).values_list('user_id', flat=True))
            print(excluded_users)
            
            members_in_proyect = list(Member.objects.filter(proyect=kwargs['instance'].id).values_list('user_id', flat=True))
            
            excluded_users = [user_id for user_id in excluded_users if user_id  in members_in_proyect]
            
            excluded_users.append(proyect_owner.id)  # Excluye al creador del proyecto
            users = User.objects.exclude(id__in=excluded_users)
            self.fields['user'].choices = [(user.id, user.first_name) for user in users]
    user = forms.TypedChoiceField(
        choices=[],  
        required=False,
        label="Miembros disponibles",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Member
        fields = ('user','is_admin')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }
      
        

class TaskCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            proyect_id = kwargs['instance'].id
            members_proyect_available = Member.objects.filter(proyect__id=proyect_id)
            list(members_proyect_available)
            #print(f"MEIMBEROS {members_proyect_available}")
            if members_proyect_available is not None:
                print([(member.id, member.user.first_name) for member in members_proyect_available])
                self.fields['asigned_at'].choices = [(member.id, member.user.first_name) for member in members_proyect_available]
                
    def save(self, *args, **kwargs):
        # Verifica si el parámetro 'from_form' está presente y es True
            # El método save() se llamó desde el formulario

        # Llama al método save() original del modelo
            super().save(*args, **kwargs)
            
    asigned_at = forms.TypedChoiceField(
        choices=[],
        required=False,
        label="La tarea sera asignada a:"
    )
    class Meta:
        model = Task
        fields = ("title","description","asigned_at")
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción', 'rows': 3}),
            'asigned_at': forms.Select(attrs={'class': 'form-control'})
        }

class UpdateTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            proyect_id = kwargs['instance'].proyect.id
            print(f"IDE EL POYRE {proyect_id}")
            members_proyect_available = Member.objects.filter(proyect__id=proyect_id)
            list(members_proyect_available)
            #print(f"MEIMBEROS {members_proyect_available}")
            if members_proyect_available is not None:
                print([(member.id, member.user.first_name) for member in members_proyect_available])
                self.fields['asigned_at'].choices = [(member.id, member.user.first_name) for member in members_proyect_available]
                
    def clean_asigned_at(self):
        asigned_at_id = self.cleaned_data.get('asigned_at')
        try:
            member = Member.objects.get(id=asigned_at_id)
            return member
        except Member.DoesNotExist:
            raise forms.ValidationError("No se puede asignar la tarea a un miembro inexistente.")
        
    def save(self, *args, **kwargs):
        # Verifica si el parámetro 'from_form' está presente y es True
            # El método save() se llamó desde el formulario

        # Llama al método save() original del modelo
            super().save(*args, **kwargs)
            
    asigned_at = forms.TypedChoiceField(
        choices=[],
        required=False,
        label="La tarea sera asignada a:"
    )
    class Meta:
        model = Task
        fields = ("title","description","asigned_at")
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción', 'rows': 3}),
            'asigned_at': forms.Select(attrs={'class': 'form-control'})
        }
        
class CompleTask(forms.ModelForm):
    class Meta:
        fields = ("completed",)
        widgets = {
            'completed': forms.BooleanField()
        }
        
class MemberRolForm(forms.ModelForm):
   class Meta:
       model = Member
       fields = ("is_admin",)