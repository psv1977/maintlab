from django.core.exceptions import PermissionDenied


def get_user_organization(user):
    try:
        return user.organization_membership.organization
    except user.organization_membership.RelatedObjectDoesNotExist as error:
        raise PermissionDenied("El usuario no tiene una empresa asignada.") from error
