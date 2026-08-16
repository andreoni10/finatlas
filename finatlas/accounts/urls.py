from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.FinAtlasLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("painel/", views.post_login_redirect, name="post_login_redirect"),
    path("painel/financeiro/", views.FinanceiroHomeView.as_view(), name="financeiro_home"),
    path("painel/assessor/", views.AssessorHomeView.as_view(), name="assessor_home"),
    path("financeiro/assessores/", views.AdvisorListView.as_view(), name="advisor_list"),
    path("financeiro/assessores/novo/", views.AdvisorCreateView.as_view(), name="advisor_create"),
    path("financeiro/assessores/<int:pk>/editar/", views.AdvisorUpdateView.as_view(), name="advisor_update"),
]