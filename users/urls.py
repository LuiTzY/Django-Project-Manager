from django.urls import path
from . import views
#urls de las acciones del usuario
urlpatterns = [
    path("login/" , views.singup, name="login"),
    path("singin/", views.singin, name="singin"),
    path('logout/',views.signout, name="logout"),
    path("profile/",views.profile, name="profile"),
    path("edit-account/", views.editAccount, name="edit-account"),
    path("delete-account/", views.deleteAccount, name="delete-account"),
    path('home/',views.home, name="home")
]