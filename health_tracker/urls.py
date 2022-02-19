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
    path("test_forms", views.test_forms, name="test_forms"),
    # path("media/<str:id>/<str:name>",views.test2,name="mediaa")
    path("view_files/<str:wbid>", views.view_files, name="view_files"),
    path('get_file/<str:wbid>', views.get_file, name="get_file")
]