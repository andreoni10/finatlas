from django.urls import path

from . import views

urlpatterns = [
    path("empresas/", views.CompanyListView.as_view(), name="company_list"),
    path("empresas/nova/", views.CompanyCreateView.as_view(), name="company_create"),
    path("empresas/<int:pk>/editar/", views.CompanyUpdateView.as_view(), name="company_update"),
    path("empresas/<int:pk>/status/", views.CompanyToggleActiveView.as_view(), name="company_toggle_active"),

    path("produtos/", views.ProductListView.as_view(), name="product_list"),
    path("produtos/novo/", views.ProductCreateView.as_view(), name="product_create"),
    path("produtos/<int:pk>/editar/", views.ProductUpdateView.as_view(), name="product_update"),
    path("produtos/<int:pk>/status/", views.ProductToggleActiveView.as_view(), name="product_toggle_active"),
]