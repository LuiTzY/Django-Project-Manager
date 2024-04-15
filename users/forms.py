from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={
            'class':'form-control',
            'placeholder':'Introduce tu contraseña',
            'minlength':'4'
        }
    ))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(
         attrs={
            'class':'form-control',
            'placeholder':'Confirme su contraseña',
            'minlength':'4'
        }
    ))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Introduzca su nombre',
                    'minlength':'4'
                    
                    }
                ),
            'last_name': forms.TextInput(
                attrs={
                'class':'form-control',
                'placeholder':'Introduzca sus apellidos',
                'minlength':'4'
                }
                                         ),
            'email': forms.EmailInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Introduzca su correo electronico'
                    }
                )
        }
        
    
    def clean_password2(self):
        # Validación para asegurarse de que las contraseñas coincidan
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if  password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password1
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificar si el correo electrónico ya existe en la base de datos
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class AunthenticaUser(forms.ModelForm):
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificar si el correo electrónico ya existe en la base de datos
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No existe una cuenta asociada a ese correo electrónico.")
        return email

    class Meta:
        model = User
        fields = ("email","password")
        widgets = {
            'email': forms.EmailInput(attrs={
                'class':'form-control mt-3',
                'placeholder':'Introduce tu correo'
            }),
            'password':forms.PasswordInput(attrs={
                'class':'form-control mt-3',
                'placeholder':"Introduce tu contraseña"
            })
        }
class UpdateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Introduzca su nombre',
                    'minlength':'4'
                    
                    }
                ),
            'last_name': forms.TextInput(
                attrs={
                'class':'form-control',
                'placeholder':'Introduzca sus apellidos',
                'minlength':'4'
                }
                                         )
        }