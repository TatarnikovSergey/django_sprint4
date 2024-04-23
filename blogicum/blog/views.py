from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (CreateView, UpdateView, DetailView,
                                  ListView, DeleteView)

from .forms import PostForm, CommentForm
from .mixins import PublishedMixin, OnlyAuthorPostMixin, OnlyAuthorCommentMixin
from .models import Post, Category


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

    def get_object(self, queryset=None):
        post = get_object_or_404(
            Post, pk=self.kwargs[self.pk_url_kwarg]
        )
        if post.author != self.request.user:
            return get_object_or_404(
                Post.objects.filter(
                    pub_date__lt=timezone.now(),
                    is_published=True,
                    category__is_published=True,
                ),
                pk=self.kwargs[self.pk_url_kwarg],
            )
        return post


class CategoryView(ListView):
    """Страницы категории."""

    template_name = 'blog/category.html'
    paginate_by = settings.SHOW_POSTS

    def get_object(self):
        return get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )

    def get_queryset(self):
        category = self.get_object()
        return PublishedMixin.get_queryset(self).filter(
            category=category
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Добавление новой публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class PostEditView(OnlyAuthorPostMixin, UpdateView):
    """Редактирование публикации."""

    pass


class PostDeleteView(OnlyAuthorPostMixin, DeleteView):
    """Удаление публикации."""

    def get_context_data(self, **kwargs):
        instance = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        context = super().get_context_data(**kwargs)
        form = PostForm(instance=instance)
        context['form'] = form
        return context

    success_url = reverse_lazy('blog:index')


class Profile(ListView):
    """Страница профиля автора публикаций."""

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
            return PublishedMixin.get_queryset(self.queryset
                                               ).filter(author=self.author)
        return posts.annotate(comment_count=Count('comments'))


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(OnlyAuthorCommentMixin, UpdateView):
    """Редактирование комментария к публикации."""

    pass


class CommentDeleteView(OnlyAuthorCommentMixin, DeleteView):
    """Удаление комментария к публикации."""

    pass


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    """Изменение данных пользователя."""

    model = User
    fields = ('username', 'first_name', 'last_name', 'email')
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})
