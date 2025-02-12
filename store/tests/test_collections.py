from rest_framework import status
import pytest


@pytest.fixture
def create_collection(api_client):
    def perform_create(data):
        return api_client.post('/store/collections/', data)
    return perform_create


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        # Arrange
        ...
        # Act
        response = create_collection(data={'title': 'a'})

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticated_client, create_collection):
        authenticated_client()

        response = create_collection(data={'title': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticated_client, create_collection):
        authenticated_client(is_staff=True)
        response = create_collection(data={'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
    
    def test_if_data_is_valid_returns_201(self, authenticated_client, create_collection):
        authenticated_client(is_staff=True)
        response = create_collection(data={'title': 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
