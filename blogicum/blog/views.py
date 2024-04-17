from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView, \
    DeleteView

from .forms import PostForm, CommentForm
from .models import Post, Category


class OnlyAuthorMixin:
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user:
            return redirect('blog:post_detail',
                            post_id=self.kwargs[self.pk_url_kwarg])
        return super().dispatch(request, *args, **kwargs)


# def index(request):
#     """Функция обработки запроса по адресу главной станицы."""
#     template_name = 'blog/index.html'
#     post_list = Post.objects.all().order_by(
#         '-pub_date', 'title')[:settings.SHOW_POSTS]
#     context = {'page_obj': post_list}
#     # context = {'post_list': post_list}
#     return render(request, template_name, context)
class IndexView(ListView):
    """Обработка запроса по адресу главной станицы."""
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.SHOW_POSTS


# def post_detail(request, post_pk):
#     """Функция обработки запроса по адресу /posts/<int:id>/."""
#     template_name = 'blog/detail.html'
#     post = get_object_or_404(Post.objects.all(), id=post_pk, )
#     context = {'post': post}
#     return render(request, template_name, context)
class PostDetailView(DetailView):
    pk_url_kwarg = 'post_id'
    model = Post
    template_name = 'blog/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


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


# def post_create(request):
#     template_name = 'blog/create.html'
#     form = PostForm(request.POST or None, files=request.FILES or None,)
#     if form.is_valid():
#         post = form.save(commit=False)
#         post.author = request.user
#         post.save()
#         return redirect('blog:index')
#     return render(request, template_name, {'form': form})
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


@login_required
def add_comment(request, post_id):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    post = get_object_or_404(Post, pk=post_id)
    # Функция должна обрабатывать только POST-запросы.
    form = CommentForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        comment = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        comment.author = request.user
        # В поле birthday передаём объект дня рождения.
        comment.post = post
        # Сохраняем объект в БД.
        comment.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('blog:post_detail', pk=post_id)
    # return redirect('blog:post_detail', pk=post_id)
