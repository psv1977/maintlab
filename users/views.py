from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from .forms import (
    OrganizationRegistrationForm,
    OrganizationRutForm,
    PublicUserRegistrationForm,
    UserCreateForm,
    UserForm,
    UserGroupsForm,
    UserPasswordForm,
)
from organizations.models import Comuna, Organization, OrganizationInvitation
from organizations.tenant import get_user_organization


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class RegistrationStartView(FormView):
    template_name = "users/registration_start.html"
    form_class = OrganizationRutForm

    def form_valid(self, form):
        organization = Organization.objects.filter(rut=form.cleaned_data["rut"]).first()
        if organization:
            self.request.session["registration_organization_id"] = organization.pk
            self.request.session["registration_new_organization"] = False
            return redirect("users:register-user")
        self.request.session["registration_organization_rut"] = form.cleaned_data["rut"]
        return redirect("users:register-organization")


class OrganizationRegistrationView(FormView):
    template_name = "users/organization_registration.html"
    form_class = OrganizationRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if "registration_organization_rut" not in request.session:
            return redirect("users:register")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {"rut": self.request.session["registration_organization_rut"]}

    def form_valid(self, form):
        organization = form.save()
        self.request.session["registration_organization_id"] = organization.pk
        self.request.session["registration_new_organization"] = True
        self.request.session.pop("registration_organization_rut", None)
        return redirect("users:register-user")


class PublicUserRegistrationView(FormView):
    template_name = "users/public_user_registration.html"
    form_class = PublicUserRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        self.organization = get_object_or_404(
            Organization, pk=request.session.get("registration_organization_id")
        )
        self.is_first_user = request.session.get("registration_new_organization", False)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        kwargs["requires_invitation"] = not self.is_first_user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["is_first_user"] = self.is_first_user
        return context

    def form_valid(self, form):
        with transaction.atomic():
            invitation = None
            if not self.is_first_user:
                invitation = OrganizationInvitation.objects.select_for_update().filter(
                    organization=self.organization,
                    code=form.cleaned_data["invitation_code"],
                ).first()
                if not invitation or not invitation.is_available:
                    form.add_error("invitation_code", "El código de invitación expiró, fue revocado o ya fue utilizado.")
                    return self.form_invalid(form)
            self.object = form.save(commit=False)
            self.object.is_staff = self.is_first_user
            self.object.save()
            membership = self.object.organization_membership
            membership.organization = self.organization
            membership.save(update_fields=["organization"])
            if invitation:
                invitation.used_by = self.object
                invitation.used_at = timezone.now()
                invitation.save(update_fields=["used_by", "used_at"])
        login(self.request, self.object)
        self.request.session.pop("registration_organization_id", None)
        self.request.session.pop("registration_new_organization", None)
        return redirect("dashboard:index")


class InvitationListView(StaffRequiredMixin, ListView):
    model = OrganizationInvitation
    template_name = "users/invitation_list.html"
    context_object_name = "invitations"

    def get_queryset(self):
        return OrganizationInvitation.objects.filter(organization=get_user_organization(self.request.user))


class InvitationCreateView(StaffRequiredMixin, View):
    def post(self, request):
        OrganizationInvitation.objects.create(
            organization=get_user_organization(request.user), created_by=request.user
        )
        return redirect("users:invitations")


class InvitationRevokeView(StaffRequiredMixin, View):
    def post(self, request, pk):
        invitation = get_object_or_404(
            OrganizationInvitation,
            pk=pk,
            organization=get_user_organization(request.user),
        )
        if invitation.is_available:
            invitation.revoked_at = timezone.now()
            invitation.save(update_fields=["revoked_at"])
        return redirect("users:invitations")


class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ["username"]

    def get_queryset(self):
        return User.objects.filter(organization_membership__organization=get_user_organization(self.request.user)).order_by("username")


class UserDetailView(StaffRequiredMixin, DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "user_obj"

    def get_queryset(self):
        return User.objects.filter(organization_membership__organization=get_user_organization(self.request.user))


class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "users/user_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["can_manage_staff"] = self.request.user.is_superuser
        return kwargs

    def get_success_url(self):
        return reverse("users:detail", args=[self.object.pk])

    def form_valid(self, form):
        response = super().form_valid(form)
        membership = self.object.organization_membership
        membership.organization = get_user_organization(self.request.user)
        membership.save(update_fields=["organization"])
        return response


class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/user_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["can_manage_staff"] = self.request.user.is_superuser
        return kwargs

    def get_success_url(self):
        return reverse("users:detail", args=[self.object.pk])

    def get_queryset(self):
        return User.objects.filter(organization_membership__organization=get_user_organization(self.request.user))


class UserGroupsUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserGroupsForm
    template_name = "users/user_groups_form.html"
    success_url = "/users/"

    def get_queryset(self):
        return User.objects.filter(organization_membership__organization=get_user_organization(self.request.user))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.object
        return kwargs

    def form_valid(self, form):
        from django.contrib.auth.models import Group
        group_pks = form.cleaned_data["groups"]
        groups = Group.objects.filter(pk__in=group_pks)
        self.object.groups.set(groups)
        return redirect(self.get_success_url())


class UserPasswordUpdateView(StaffRequiredMixin, FormView):
    form_class = UserPasswordForm
    template_name = "users/user_password_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=kwargs["pk"], organization_membership__organization=get_user_organization(request.user))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user_obj
        return kwargs

    def get_success_url(self):
        return reverse("users:detail", args=[self.user_obj.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_obj"] = self.user_obj
        return context

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


def comunas_por_region(request):
    region_id = request.GET.get("region_id")
    if not region_id:
        return JsonResponse([], safe=False)
    comunas = Comuna.objects.filter(region_id=region_id).values_list("id", "name")
    return JsonResponse(list(comunas), safe=False)
