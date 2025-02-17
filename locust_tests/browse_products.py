import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings')
django.setup()

from random import randint
from django.urls import reverse
from locust import HttpUser, task, between


class WebUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        response = self.client.post(reverse('cart-list'))
        result = response.json()
        self.cart_id = result['id']

    @task(2)
    def view_products(self):
        collection_id = randint(3, 6)
        self.client.get(reverse('products-list'), params={'collection_id': collection_id}, name='/store/products')


    @task(4)
    def view_product(self):
        product_id = randint(1, 1000)
        self.client.get(reverse('products-detail', kwargs={'pk': product_id}), name='/store/products/:id/')


    @task(1)
    def add_to_cart(self):
        product_id = randint(1, 10)
        self.client.post(
            reverse('cart-items-list', kwargs={'cart_pk': self.cart_id}),
            json={'product_id': product_id, 'quantity': 1},
            name='/store/carts/items'
        )