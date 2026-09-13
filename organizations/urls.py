from django.urls import path

from .views import CustomerCreateView

app_name = "organizations"

urlpatterns = [path("customers/new/", CustomerCreateView.as_view(), name="customer-create")]
