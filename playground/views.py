from django.core.mail import EmailMessage, BadHeaderError
from django.shortcuts import render


def say_hello(request):
    try:
        email = EmailMessage('subject', 'message', 'from@storefront.com', ['john.smith@domain.com'])
        email.attach_file('playground/static/images/Me.jpg')
        email.send()
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {'name': 'Mosh'})
