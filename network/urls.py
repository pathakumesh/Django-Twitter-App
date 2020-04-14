
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user_info/<int:user_id>", views.user_info, name="user_info"),
    path("create_post", views.create_post, name="create_post"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("my_posts", views.my_posts, name="my_posts"),
    path("following_posts", views.following_posts, name="following_posts"),
]
