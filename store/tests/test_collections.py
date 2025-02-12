from django.urls import reverse
from rest_framework import status
from model_bakery import baker
import pytest

from store.models import Collection


@pytest.fixture
def create_collection(api_client):
    def perform_create(data):
        return api_client.post('/store/collections/', data)
    return perform_create


@pytest.fixture
def update_collection(api_client):
    def perform_update(collection_id, data):
        return api_client.patch(reverse('collection-detail', kwargs={'pk': collection_id}), data)
    return perform_update


@pytest.fixture
def delete_collection(api_client):
    def perform_delete(collection_id):
        return api_client.delete(reverse('collection-detail', kwargs={'pk': collection_id}))
    return perform_delete


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


@pytest.mark.django_db
class TestRetireveCollection:

    def test_if_collection_does_not_exists_returns_404(self, api_client):
        response = api_client.get(reverse('collection-detail', kwargs={'pk': 0}))

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(reverse('collection-detail', kwargs={'pk': collection.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }


    def test_if_list_all_collections_returns_200(self, api_client):
        collections = baker.make(Collection, _quantity=3)

        response = api_client.get(reverse('collection-list'))

        assert response.status_code == status.HTTP_200_OK
        for collection, response_item in zip(collections, response.data):
            assert collection.id == response_item['id']
            assert collection.title == response_item['title']


@pytest.mark.django_db
class TestUpdateCollection:

    def test_if_user_is_anonymous_returns_401(self, update_collection):
        response = update_collection(collection_id=0, data={'title': 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_returns_403(self, authenticated_client, update_collection):
        authenticated_client()

        response = update_collection(collection_id=0, data={'title': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_collection_does_not_exists_returns_404(self, authenticated_client, update_collection):
        authenticated_client(is_staff=True)

        response = update_collection(collection_id=0, data={'title': 'a'})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


    def test_if_data_is_invalid_returns_400(self, authenticated_client, update_collection):
        authenticated_client(is_staff=True)
        collection = baker.make(Collection)

        response = update_collection(collection_id=collection.id, data={'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
    

    def test_if_data_is_valid_returns_200(self, authenticated_client, update_collection):
        authenticated_client(is_staff=True)
        collection = baker.make(Collection)

        new_title = 'a'
        response = update_collection(collection_id=collection.id, data={'title': new_title})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': new_title,
            'products_count': 0
        }


@pytest.mark.django_db
class TestDeleteCollection:

    def test_if_user_is_anonymous_returns_401(self, delete_collection):
        response = delete_collection(collection_id=0)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_returns_403(self, authenticated_client, delete_collection):
        authenticated_client()

        response = delete_collection(collection_id=0)

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_collection_does_not_exists_returns_404(self, authenticated_client, delete_collection):
        authenticated_client(is_staff=True)

        response = delete_collection(collection_id=0)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


    def test_if_deleted_returns_204(self, authenticated_client, delete_collection):
        authenticated_client(is_staff=True)
        collection = baker.make(Collection)

        response = delete_collection(collection_id=collection.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT
