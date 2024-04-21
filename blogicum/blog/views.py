from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DetailView, ListView, \
    DeleteView

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment


class OnlyAuthorCommentMixin(LoginRequiredMixin): #UserPassesTestMixin):
    model = Comment
    form_class = CommentForm
    # pk_field = 'comment_id'
    # pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})
    #
    def get_object(self):
        return get_object_or_404(
            Comment.objects.filter(post=self.kwargs['post_id']),
            pk=self.kwargs['comment_id']
        )
    def dispatch(self, request, *args, **kwargs):
        # self.get_object
        #     get_object_or_404(
        #     Comment.objects.filter(post=self.kwargs['post_id']),
        #     pk=self.kwargs['comment_id']
        # )
        if self.get_object().author != request.user:
            # return reverse('blog:post_detail',
            #                kwargs={'post_id': self.kwargs.get('post_id')})
            return redirect('blog:post_detail',
                            post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
    # def test_func(self):
    #     object = self.get_object()
    #     return object.author == self.request.user
    #
    # def handle_no_permission(self):
    #     object = self.get_object()
    #     if not self.request.user.is_authenticated:
    #         return redirect('login')
    #     return redirect('blog:post_detail', post_id=object.id, permanent=True)


class OnlyAuthorPostMixin(LoginRequiredMixin):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user:
            return redirect('blog:post_detail',
                            post_id=self.kwargs[self.pk_url_kwarg])
        return super().dispatch(request, *args, **kwargs)

    # def test_func(self, *args, **kwargs):
    #     object = self.get_object()
    #     if object.author != self.request.user:
    #         return redirect('blog:post_detail',
    #                             post_id=self.kwargs[self.pk_url_kwarg])
    #         # return super().dispatch(request, *args, **kwargs)
    #     return object.author == self.request.user


class PublishedMixin:

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'author', 'location', 'category'
        ).filter(
            pub_date__lt=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).order_by(
            '-pub_date'
        ).annotate(
            comment_count=Count('comments')
        ).all()


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


#


class PostCreateView(LoginRequiredMixin, CreateView):
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
    # model = Post
    # form_class = PostForm
    # pk_url_kwarg = 'post_id'
    # template_name = 'blog/create.html'
    pass


class PostDeleteView(OnlyAuthorPostMixin, DeleteView):
    # model = Post
    # form_class = PostForm
    # pk_url_kwarg = 'post_id'
    # template_name = 'blog/create.html'
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
            # posts = posts.filter(
            #     is_published=True,
            #     pub_date__lte=timezone.now(),
            #     category__is_published=True).order_by('-pub_date').annotate(
            #     comment_count=Count('comments'))
            return PublishedMixin.get_queryset(self.queryset)  # posts
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


class CommentUpdateView(OnlyAuthorCommentMixin, UpdateView):
    # model = Comment
    # form_class = CommentForm
    # pk_field = 'comment_id'
    # pk_url_kwarg = 'comment_id'
    # template_name = 'blog/comment.html'
    #
    # def get_success_url(self):
    #     return reverse('blog:post_detail',
    #                    kwargs={'post_id': self.kwargs.get('post_id')})
    pass


class CommentDeleteView(OnlyAuthorCommentMixin, DeleteView):
    # model = Comment
    # form_class = CommentForm
    # pk_field = 'comment_id'
    # pk_url_kwarg = 'comment_id'
    # template_name = 'blog/comment.html'
    #
    # def get_success_url(self):
    #     return reverse('blog:post_detail',
    #                    kwargs={'post_id': self.kwargs.get('post_id')})
    pass


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email')
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})

# class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
#     """
#     Изменение пароля пользователя
#     """
#     model = User
#     template_name = 'blog/user.html'
#
#     def get_object(self, queryset=None):
#         return self.request.user
#
#     def get_success_url(self):
#         return reverse('blog:profile',
#                        kwargs={'username': self.request.user})
