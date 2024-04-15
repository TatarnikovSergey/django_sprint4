from django.db.models import Manager
from django.utils.timezone import now


class PostManager(Manager):
    """Менеджер объектов модели публикация"""

    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now()
        ).select_related('author', 'location', 'category')
