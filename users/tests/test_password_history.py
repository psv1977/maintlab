import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from users.forms import UserPasswordForm
from users.models import PasswordHistory


@pytest.mark.django_db
def test_new_user_password_is_stored_in_history():
    user = User.objects.create_user(username="juan", password="Initial123!")
    assert PasswordHistory.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_password_form_rejects_previous_password():
    user = User.objects.create_user(username="juan", password="Initial123!")
    form = UserPasswordForm(
        user=user,
        data={
            "new_password1": "Initial123!",
            "new_password2": "Initial123!",
        },
    )

    assert not form.is_valid()
    assert "anterior" in str(form.errors)


@pytest.mark.django_db
def test_password_form_stores_new_password_in_history():
    user = User.objects.create_user(username="juan", password="Initial123!")
    form = UserPasswordForm(
        user=user,
        data={
            "new_password1": "NewPassword123!",
            "new_password2": "NewPassword123!",
        },
    )

    assert form.is_valid()
    form.save()
    assert PasswordHistory.objects.filter(user=user).count() == 2
