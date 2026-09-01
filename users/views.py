from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import UserCreateForm, UserForm, UserGroupsForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 20


class UserDetailView(StaffRequiredMixin, DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "user_obj"


class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "users/user_form.html"

    def get_success_url(self):
        return reverse("users:detail", args=[self.object.pk])


class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/user_form.html"

    def get_success_url(self):
        return reverse("users:detail", args=[self.object.pk])


class UserGroupsUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserGroupsForm
    template_name = "users/user_groups_form.html"
    success_url = "/users/"

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
