from django.shortcuts import render


def about(request):
    """Функция обработки запроса по адресу pages/about/."""
    template_name = 'pages/about.html'
    return render(request, template_name)


def rules(request):
    """Функция обработки запроса по адресу pages/rules/."""
    template_name = 'pages/rules.html'
    return render(request, template_name)
