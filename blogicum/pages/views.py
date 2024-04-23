from django.shortcuts import render
from django.views.generic import TemplateView
from http import HTTPStatus


class About(TemplateView):
    """Обработка запроса по адресу pages/about/."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """Обработка запроса по адресу pages/rules/."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Обработка ошибки 404 кастомной страницей."""
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def csrf_failure(request, reason=''):
    """Обработка ошибки 403 кастомной страницей."""
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def server_error(request):
    """Обработка ошибки 500 кастомной страницей."""
    return render(request, 'pages/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)
