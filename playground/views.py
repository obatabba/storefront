import requests
from django.core.cache import cache
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import notify_customers


def say_hello(request):
    notify_customers.delay('Hello')
    cache.clear()

    return render(request, 'hello.html', {'name': 'Mosh'})


class SlowEndpoint(APIView):
    @method_decorator(cache_page(5 * 60))
    def get(self, request):
        response = requests.get('https://httpbin.org/delay/2')
        data = response.json()
        return Response(data)
