from django.urls import path

from . import views


app_name = "equipment"

urlpatterns = [
    path("", views.equipment_list, name="list"),
    path("new/", views.equipment_create, name="create"),
    path("<int:pk>/", views.equipment_detail, name="detail"),
    path("<int:pk>/edit/", views.equipment_update, name="update"),
    path("<int:pk>/retire/", views.equipment_retire, name="retire"),
]
