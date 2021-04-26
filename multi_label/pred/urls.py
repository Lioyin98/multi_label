from django.urls import path
from pred import views

urlpatterns = [
    path("index/", views.index),
    path("register/", views.user_register),
    path("login/", views.user_login),
    path("change_passwd/", views.user_change_passwd),
    path("history_list/", views.history_list),
    path("compute/", views.compute),
    path("logout/", views.user_logout)
]
