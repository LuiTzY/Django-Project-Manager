from django.shortcuts import render,redirect
from .models import User
from .forms import UserForm, AunthenticaUser, UpdateAccountForm
from django.db import IntegrityError
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from proyects.models import Proyect,Member

#vista principal de la app
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
    #si obtiene el usuario
    user = User.objects.get(id=request.user.id)
    #se obtienen los proyectos del usuario
    proyects = Proyect.objects.filter(project_owner__id=user.id)
    #se obtienen los proyectos en los que el usuario ha sido agregado
    user_external_proyects = Member.objects.filter(user__id=user.id)
    if  user is not None:
        #si el usuario es valido, se redirecciona al perfil
        return render(request, "profile.html",{"proyects":proyects,"proyect_members":user_external_proyects})

@login_required
def editAccount(request):
    #si es por get la solicitud
    if request.method == "GET":
        #se renderiza el formulario
        return render(request, "edit.html", {"form":UpdateAccountForm()})
    else:
        #se actualiza el usuario, pasando la instancia del usuario en la solicitud
        updateForm = UpdateAccountForm(data=request.POST,instance=request.user)
        #si es valido
        if updateForm.is_valid():
            #se guarda
            updateForm.save()
            #se crea un mensaje de exito
            messages.success(request, '¡Tu cuenta ha sido actualizada correctamente!')  
            #se redireccion a el perfil
            return redirect("profile")
        else:
            #se crea un error
            messages.error(request, 'Hubo un error al actualizar tu cuenta, Por favor vuelva a intentarlo.')

@login_required
def deleteAccount(request):
    request.user.delete()
        #Se cierra la sesion del usuario que estaba en la request
    logout(request)
        #Creamos un mensaje flash de que se pudo eliminar la cuenta correctamente
    messages.success(request, '¡Tu cuenta ha sido eliminada correctamente!')
    return redirect('login') 
        
        