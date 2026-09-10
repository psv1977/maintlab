from django.urls import path

from . import views


app_name = "users"

urlpatterns = [
    path("register/", views.RegistrationStartView.as_view(), name="register"),
    path("register/organization/", views.OrganizationRegistrationView.as_view(), name="register-organization"),
    path("register/user/", views.PublicUserRegistrationView.as_view(), name="register-user"),
    path("api/comunas/", views.comunas_por_region, name="comunas-por-region"),
    path("invitations/", views.InvitationListView.as_view(), name="invitations"),
    path("invitations/new/", views.InvitationCreateView.as_view(), name="invitation-create"),
    path("invitations/<int:pk>/revoke/", views.InvitationRevokeView.as_view(), name="invitation-revoke"),
    path("", views.UserListView.as_view(), name="list"),
    path("new/", views.UserCreateView.as_view(), name="create"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.UserUpdateView.as_view(), name="update"),
    path("<int:pk>/groups/", views.UserGroupsUpdateView.as_view(), name="groups"),
    path("<int:pk>/password/", views.UserPasswordUpdateView.as_view(), name="password"),
]
