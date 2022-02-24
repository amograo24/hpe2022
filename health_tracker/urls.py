from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path('test',views.test,name="test"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout",views.logout_view, name="logout"),
    # path("myprofile",views.myprofile, name="myprofile"),
    path("notifications", views.notifications, name="notifications"),
    path("",views.index,name="index"),
    path("user/<str:id>",views.other_profile,name="other_profile"),
    path("upload",views.upload_file,name="upload_file"),
    # path("test_forms", views.test_forms, name="test_forms"),
    path("media/<str:wbid>/<str:name>",views.file_page,name="file_page"),
    path('get_file/<str:wbid>/<str:name>', views.get_file, name="get_file"),
    path("myfiles",views.myfiles,name="myfiles")
    # path("media")
]