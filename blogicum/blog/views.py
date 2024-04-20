from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.timezone import now
from django.views.generic import CreateView, UpdateView, DetailView, ListView, \
    DeleteView

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment


class OnlyAuthorMixin:
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user:
            return redirect('blog:post_detail',
                            post_id=self.kwargs[self.pk_url_kwarg])
        return super().dispatch(request, *args, **kwargs)


class PublishedMixin:
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now()
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments')).select_related(
            'author', 'location', 'category')


class IndexView(PublishedMixin, ListView):
    """Обработка запроса по адресу главной станицы."""
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.SHOW_POSTS


class PostDetailView(DetailView):
    """Детализация поста"""
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


class Profile(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = settings.SHOW_POSTS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        posts = self.author.posts.select_related(
            'author', 'location', 'category').order_by('-pub_date')
        if self.author != self.request.user:
            posts = posts.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True).order_by('-pub_date').annotate(
                comment_count=Count('comments'))
            return posts
        return posts


@login_required
def add_comment(request, post_id):
    # Получаем объект  или выбрасываем 404 ошибку.
    post = get_object_or_404(Post, pk=post_id)
    # Функция должна обрабатывать только POST-запросы.
    form = CommentForm(request.POST)
    if form.is_valid():
        # Создаём объект, но не сохраняем его в БД.
        comment = form.save(commit=False)
        # В поле author передаём объект автора.
        comment.author = request.user
        # В поле comment передаём объект.
        comment.post = post
        # Сохраняем объект в БД.
        comment.save()
    # Перенаправляем пользователя назад, на страницу поста.
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_field = 'comment_id'
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    pk_field = 'comment_id'
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
#     success_url = reverse_lazy('blog:index')

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})
