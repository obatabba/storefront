from operator import attrgetter, itemgetter
from django.urls import reverse
from rest_framework import status
from model_bakery import baker
import pytest

from store.models import Collection, Product


@pytest.fixture
def create_product(api_client):
    def perform_create(data):
        return api_client.post(reverse('products-list'), data, format='json')
    return perform_create


@pytest.fixture
def update_product(api_client):
    def perform_update(product_id, data):
        return api_client.patch(reverse('products-detail', kwargs={'pk': product_id}), data, format='json')
    return perform_update


@pytest.fixture
def delete_product(api_client):
    def perform_delete(product_id):
        return api_client.delete(reverse('products-detail', kwargs={'pk': product_id}))
    return perform_delete


@pytest.mark.django_db
class TestCreateProduct:

    def test_if_user_is_anonymous_returns_401(self, create_product):
        response = create_product(data={})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_returns_403(self, authenticated_client, create_product):
        authenticated_client()

        response = create_product(data={})

        assert response.status_code == status.HTTP_403_FORBIDDEN


    @pytest.mark.parametrize(
        "invalid_payload, expected_error_fields",
        [
            ({'description': {}}, ['title', 'slug', 'description', 'unit_price', 'inventory', 'collection']),
            ({'collection': 'inexistent collection'}, ['collection']),
            ({'unit_price': -1, 'inventory': -1}, ['unit_price', 'inventory']),
            ({'unit_price': '9999.999'}, ['unit_price'])
        ]
    )
    def test_if_data_is_invalid_returns_400(self, authenticated_client, create_product, invalid_payload, expected_error_fields):
        authenticated_client(is_staff=True)

        response = create_product(data=invalid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        for field in expected_error_fields:
            assert field in response.data


    def test_if_data_is_valid_returns_201(self, authenticated_client, create_product):
        authenticated_client(is_staff=True)
        collection = baker.make(Collection)

        product = {
            'title': 'a',
            'slug': 'b',
            'description': 'c',
            'unit_price': 1,
            'inventory': 1,
            'collection': collection.id,
        }
        response = create_product(data=product)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == product['title']
        assert response.data['slug'] == product['slug']
        assert response.data['description'] == product['description']
        assert response.data['unit_price'] == product['unit_price']
        assert response.data['inventory'] == product['inventory']
        assert response.data['collection'] == product['collection']
        
        # Auto-populated fields
        assert 'id' in response.data
        assert 'price_with_tax' in response.data
        assert 'images' in response.data


@pytest.mark.django_db
class TestRetrieveProduct:

    def test_if_product_does_not_exists_returns_404(self, api_client):
        response = api_client.get(reverse('products-detail', kwargs={'pk': 0}))

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


    def test_if_product_exists_returns_200(self, api_client):
        product = baker.make(Product)

        response = api_client.get(reverse('products-detail', kwargs={'pk': product.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id
        assert response.data['title'] == product.title
        assert response.data['slug'] == product.slug
        assert response.data['description'] == product.description
        assert response.data['unit_price'] == product.unit_price
        assert response.data['inventory'] == product.inventory
        assert response.data['collection'] == product.collection.id
        
        # Extra fields
        assert 'price_with_tax' in response.data
        assert 'images' in response.data


    def test_if_list_all_products_returns_200(self, api_client):
        products = baker.make(Product, _quantity=3)

        response = api_client.get(reverse('products-list'))

        assert response.status_code == status.HTTP_200_OK
        # Sort the products list and the returned products by product id to ensure same ordering before comparing.
        for product, response_item in zip(sorted(products, key=attrgetter('id')), sorted(response.data['results'], key=itemgetter('id'))):
            assert response_item['id'] == product.id
            assert response_item['title'] == product.title
            assert response_item['slug'] == product.slug
            assert response_item['description'] == product.description
            assert response_item['unit_price'] == product.unit_price
            assert response_item['inventory'] == product.inventory
            assert response_item['collection'] == product.collection.id

            # Extra fields
            assert 'price_with_tax' in response_item
            assert 'images' in response_item


@pytest.mark.django_db
class TestUpdateProduct:

    def test_if_user_is_anonymous_returns_401(self, update_product):
        response = update_product(product_id=0, data={})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_returns_403(self, authenticated_client, update_product):
        authenticated_client()

        response = update_product(product_id=0, data={})

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_product_does_not_exists_returns_404(self, authenticated_client, update_product):
        authenticated_client(is_staff=True)

        response = update_product(product_id=0, data={})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


    @pytest.mark.parametrize(
        "invalid_payload, expected_error_fields",
        [
            (
                {"title": "", "description": {}, "slug": {}, "inventory": -1, "unit_price": -1, "collection": 0}, ['title', 'slug', 'description', 'unit_price', 'inventory', 'collection']
            ),
            ({'title': 'a'*256}, ['title']),
            ({'unit_price': '9999.999'}, ['unit_price'])
        ]
    )
    def test_if_data_is_invalid_returns_400(self, authenticated_client, update_product, invalid_payload, expected_error_fields):
        authenticated_client(is_staff=True)
        product = baker.make(Product)

        response = update_product(product_id=product.id, data=invalid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        for field in expected_error_fields:
            assert field in response.data
    

    def test_if_data_is_valid_returns_200(self, authenticated_client, update_product):
        authenticated_client(is_staff=True)
        product = baker.make(Product)

        new_title = 'a'
        response = update_product(product_id=product.id, data={'title': new_title})

        assert response.status_code == status.HTTP_200_OK
        assert response.data.pop('price_with_tax')
        assert response.data == {
            'id': product.id,
            'title': new_title,
            'description': product.description,
            'slug': product.slug,
            'unit_price': product.unit_price,
            'inventory': product.inventory,
            'collection': product.collection.id,
            'images': []
        }


@pytest.mark.django_db
class TestDeleteProduct:

    def test_if_user_is_anonymous_returns_401(self, delete_product):
        response = delete_product(product_id=0)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_returns_403(self, authenticated_client, delete_product):
        authenticated_client()

        response = delete_product(product_id=0)

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_product_does_not_exists_returns_404(self, authenticated_client, delete_product):
        authenticated_client(is_staff=True)

        response = delete_product(product_id=0)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


    def test_if_deleted_returns_204(self, authenticated_client, delete_product):
        authenticated_client(is_staff=True)
        product = baker.make(Product)

        response = delete_product(product_id=product.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT
