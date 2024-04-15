from django.shortcuts import render,redirect
from .models import User
from .forms import UserForm, AunthenticaUser, UpdateAccountForm
from django.db import IntegrityError
from django.contrib.auth import login,authenticate,logout
from django.shortcuts import get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from proyects.models import Proyect,Member

def home(request):
    return render(request,'layout.html')

#view para la creacion de una cuenta
def singup(request):
    
    #Datos recogidos de un formulario
    if request.method == "GET":
        #Renderizar formulario
        return render(request, "singup.html",{"form":UserForm()})
    else:
        #Recoger datos del formulario
        userForm = UserForm(request.POST)
        if userForm.is_valid():
            print(userForm.cleaned_data)
            try:
                userForm.save()
            except IntegrityError:
                print("HA OCURRIDO UN ERROR")
                messages.error("Este Correo ya esta siendo utilizado")
                return render(request, 'singup.html')
            else:
                email = userForm.cleaned_data['email']
                password = userForm.cleaned_data['password1']
                user = authenticate(request, username=email, password=password)
                login(request, user)
                return redirect("home")
        else:
            
            print("Errores en el formularios ", userForm.errors)

            return render(request, "singup.html", {"form":userForm,"welcome":True})


#View para iniciar sesion del usuario
def singin(request):
    if request.method == "GET":
        return render(request, "singin.html",{"form":AunthenticaUser()}) 
    else:
        email = request.POST['email']
        password = request.POST['password']
        print(f"Usuario creado {email} {password}\n")
        user = authenticate(request,email=email,password=password)   
        
        if user is None:
            messages.error(request,"El correo electronico o contraseña nos son validos")
            return render(request, "singin.html",{"form":AunthenticaUser(),"welcome":True})
        
        login(request,user)
        
        messages.success(request, '¡Has iniciado sesion correctamente!')
        return redirect("home")
        
#View para cerrar sesion del usuario
@login_required
def signout(request):
    try:
        logout(request)
    except Exception as e:
        messages.error(request,"No se ha podido cerrar sesion correctamente.")
    else:
        messages.success(request,"¡¡ Has cerrado sesion correctamente !!")
    return redirect('singin')

#View para cargar perfil del usuario

@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    proyects = Proyect.objects.filter(project_owner__id=user.id)
    user_external_proyects = Member.objects.filter(user__id=user.id)
    print(user_external_proyects) 
    if  user is not None:
        """if proyects is None and user_external_proyects is not None:
            return render(request, "profile.html",{"proyects":proyects,"proyect_members":user_external_proyects})
        elif proyects is not None and user_external_proyects is None:
            return render(request,"profile.html",{"proyects":proyects})
        elif proyects is None and user_external_proyects is not None:
            return render(request, "profile.html",{"proyect_members":user_external_proyects})"""
        return render(request, "profile.html",{"proyects":proyects,"proyect_members":user_external_proyects})

@login_required
def editAccount(request):
    if request.method == "GET":
        return render(request, "edit.html", {"form":UpdateAccountForm()})
    else:
        updateForm = UpdateAccountForm(data=request.POST,instance=request.user)
        if updateForm.is_valid():
            updateForm.save()
            messages.success(request, '¡Tu cuenta ha sido actualizada correctamente!')  
            return redirect("profile")
        else:
            messages.error(request, 'Hubo un error al actualizar tu cuenta, Por favor vuelva a intentarlo.')

@login_required
def deleteAccount(request):
    request.user.delete()
        #Se cierra la sesion del usuario que estaba en la request
    logout(request)
        #Creamos un mensaje flash de que se pudo eliminar la cuenta correctamente
    messages.success(request, '¡Tu cuenta ha sido eliminada correctamente!')
    return redirect('login') 
        
        