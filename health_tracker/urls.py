from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path('test',views.test,name="test"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout",views.logout_view, name="logout"),
    path("myprofile",views.myprofile, name="myprofile"),
    path("",views.index,name="index")
]

