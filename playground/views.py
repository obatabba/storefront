import logging
import requests
from django.core.cache import cache
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import notify_customers


logger = logging.getLogger(__name__)


def say_hello(request):
    notify_customers.delay('Hello')
    cache.clear()
    logger.info('Cache has been cleared.')

    return render(request, 'hello.html', {'name': 'Mosh'})


class SlowEndpoint(APIView):

    @method_decorator(cache_page(5 * 60))
    def get(self, request):
        try:
            response = requests.get('https://httpbin.org/delay/2')
            data = response.json()
        except requests.exceptions.ConnectionError:
            logger.critical('Could not reach httpbin.')
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(data)
