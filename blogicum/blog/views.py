from django.conf import settings
from django.shortcuts import get_object_or_404, render

from .models import Post, Category


def index(request):
    """Функция обработки запроса по адресу главной станицы."""
    template_name = 'blog/index.html'
    post_list = Post.objects.all().order_by(
        '-pub_date', 'title')[:settings.SHOW_POSTS]
    context = {'page_obj': post_list}
    # context = {'post_list': post_list}
    return render(request, template_name, context)


def post_detail(request, post_pk):
    """Функция обработки запроса по адресу /posts/<int:id>/."""
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post.objects.all(), id=post_pk, )
    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    """Функция обработки запроса по адресу category/<slug:category_slug>/."""
    template_name = 'blog/category.html'
    post_list = Post.objects.all().filter(category__slug=category_slug)
    category = get_object_or_404(Category.objects.only(
        'title', 'description'
    ).filter(
        is_published=True,
        slug=category_slug))
    context = {'post_list': post_list, 'category': category}
    return render(request, template_name, context)
