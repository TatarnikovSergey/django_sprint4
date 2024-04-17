from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    # path('posts/<int:post_pk>/', views.post_detail, name='post_detail'),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    # path('posts/create/', views.post_create, name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        views.PostEditView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    )
]
