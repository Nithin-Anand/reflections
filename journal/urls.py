from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    path("", views.journal_view, name="journal"),
    path("api/entries/create/", views.create_entry_view, name="create_entry"),
    path("api/entries/date/", views.get_entries_by_date, name="get_entries"),
    path(
        "api/entries/<int:entry_id>/delete/",
        views.delete_entry_view,
        name="delete_entry",
    ),
    path("api/theme/update/", views.update_theme, name="update_theme"),
    path("register/", views.register_view, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="journal/login.html", authentication_form=CustomLoginForm
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
]
