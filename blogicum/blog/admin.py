from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.defaultfilters import truncatewords

from .models import Category, Location, Post

admin.site.empty_value_display = 'Нет данных'

admin.site.unregister(Group)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Интерфейс управления моделью публикации."""

    def text_char_len(self, obj):
        """Обрезка количества слов поля "ТЕКСТ" в списке постов."""
        return truncatewords(obj.text, settings.LEN_TEXT_ADMIN_LIST)

    text_char_len.short_description = 'Текст'
    list_display = (
        'title',
        'text_char_len',
        'pub_date',
        'created_at',
        'is_published',
        'author',
        'location',
        'category'
    )
    list_editable = (
        'pub_date',
        'is_published',
        'category'
    )
    list_filter = ('category',)
    search_fields = ('title',)


class PostInline(admin.StackedInline):
    """Вставка списка постов для связанной модели."""

    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Интерфейс управления моделью категории."""

    inlines = (PostInline,)
    list_display = (
        'title',
        'is_published',
        'slug'
    )
    list_editable = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Интерфейс управления моделью местоположения."""

    inlines = (PostInline,)
    list_display = (
        'name',
        'is_published'
    )
    list_editable = ('is_published',)
