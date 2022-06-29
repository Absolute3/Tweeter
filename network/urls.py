from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newpost, name="newpost"),
    path("user/<str:username>", views.user, name="user"),
    path("following", views.following, name="following"),
    path("edit/<int:post_id>", views.editpost, name="editpost"),
    path("follow/<str:username>", views.follow, name="follow"),
    path("unfollow/<str:username>", views.unfollow, name="unfollow"),
    path('like/<int:post_id>', views.like, name='like'),
]
