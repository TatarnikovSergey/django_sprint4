from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import PostForm
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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# def post_create(request):
#     template_name = 'blog/create.html'
#     form = PostForm(request.POST or None, files=request.FILES or None,)
#     if form.is_valid():
#         post = form.save(commit=False)
#         post.author = request.user
#         post.save()
#         return redirect('blog:index')
#     return render(request, template_name, {'form': form})


class PostEditView(UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
