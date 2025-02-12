from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client: APIClient):
    def perform_authentication(**kwargs): # Here you can pass user attributes like is_staff, is_active, etc.
        return api_client.force_authenticate(user=get_user_model()(**kwargs))
    return perform_authentication