import pytest
from organizations.models import Comuna, Region


@pytest.fixture
def default_region():
    return Region.objects.first()


@pytest.fixture
def default_comuna(default_region):
    return Comuna.objects.filter(region=default_region).first()
