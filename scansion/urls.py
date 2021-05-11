from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:id>", views.index, name="index"),
    path("poem/<int:id>", views.poem, name="poem"),
    path("about", views.about, name="about"),
    path("choose_poem/<str:poet_name>", views.choose_poem, name="choose_poem"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("rescan_poem/<int:id>", views.rescan_poem, name="rescan_poem"),
    path("rescan_all", views.rescan_all, name="rescan_all")
]