from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path('test', views.test, name="test"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    # path("myprofile",views.myprofile, name="myprofile"),
    path("notifications", views.notifications, name="notifications"),
    path("", views.index, name="index"),
    path("user/<str:id>", views.other_profile, name="other_profile"),
    path("upload", views.upload_file, name="upload_file"),
    # path("test_forms", views.test_forms, name="test_forms"),
    path("media/<str:wbid>/<str:name>", views.file_page, name="file_page"),
    path('get_file/<str:wbid>/<str:name>', views.get_file, name="get_file"),
    path("myfiles", views.myfiles, name="myfiles"),
    path("health/<str:wbid>", views.health_status_function, name="health"),
    path("auth_messages", views.notification_page, name="auth_messages"), #approval messages
    path("search",views.search,name="search"),
    path("delete_file/<str:wbid>/<str:name>",views.delete_file,name="delete_file"),
    path("mydoctors_vendors",views.mydoctors_vendors,name="mydoctors_vendors"),
    path("mypatients_customers",views.mypatients_customers,name="mypatients_customers"),
    path("edit/<str:wbid>/<str:file_name>",views.edit_file,name="edit_file"),
    path("remove/<str:id>",views.remove_patient_vendor,name="remove_patient_vendor"),
    path("visit/<str:id>",views.visit_qrcode,name="visit"),
    path("gopublic",views.go_public,name="go_public"),
    path("goprivate",views.go_private,name="go_private"),
    path("search_public",views.search_public_vendors,name="search_public")
    # path("media")
]

urlpatterns += [path('states', views.StatesAPI, name="states"),
                path('getQr', views.handle_Qr)]
