from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now

from .forms import CommentForm, PostForm
from .models import Post, Comment


class OnlyAuthorCommentMixin(LoginRequiredMixin):
    """Миксин предоставления прав редактирования комментариев только автором"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

    def get_object(self):
        return get_object_or_404(
            Comment.objects.filter(post=self.kwargs['post_id']),
            pk=self.kwargs['comment_id']
        )

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail',
                            post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class OnlyAuthorPostMixin(LoginRequiredMixin):
    """Миксин предоставления прав редактирования публикаций только автором"""

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


class PublishedMixin:
    """
    Миксин представления только опубликованных постов на текущий момент
    времени, в том числе подсчет количества комментариев к публикациям.
    """

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'author', 'location', 'category'
        ).filter(
            pub_date__lt=now(),
            is_published=True,
            category__is_published=True,
        ).order_by(
            '-pub_date'
        ).annotate(
            comment_count=Count('comments')
        )
