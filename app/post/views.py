from base.paginations import DefaultPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from . import serializers
from .models import Post

User = get_user_model()


class TagsFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            tags = [tag.strip() for tag in value.split(",")]
            qs = qs.filter(tags__name__in=tags).distinct()
        return qs


class PostFilter(filters.FilterSet):
    tags = TagsFilter(field_name="tags__name")
    title = filters.CharFilter(lookup_expr="icontains")
    created_from = filters.CharFilter(field_name="created_at", lookup_expr="gte")
    created_to = filters.CharFilter(field_name="created_at", lookup_expr="lte")
    author__username = filters.CharFilter(
        field_name="author__username", lookup_expr="exact"
    )

    class Meta:
        model = Post
        fields = ["tags", "title", "created_from", "created_to", "author__username"]


class PostViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Post.objects.none()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = serializers.PostSerializer
    pagination_class = DefaultPagination

    filterset_class = PostFilter
    search_fields = ("title",)
    filter_backends = [filters.DjangoFilterBackend, drf_filters.SearchFilter]

    def get_queryset(self):
        user = self.request.user
        if (
            user
            and user.is_authenticated
            and user.username == self.request.query_params.get("author__username")  # type: ignore
        ):
            return Post.objects.filter(author=user)
        return Post.objects.filter()

    def get_object(self):
        slug = self.kwargs[self.lookup_field]
        post = get_object_or_404(Post, slug=slug)
        if (
            self.action == "retrieve"
            and post.publish_at
            and post.publish_at < timezone.now()
        ):
            return post
        if not self.request.user:
            raise PermissionDenied("Invalid access")
        if self.request.user.id != post.author_id:  # type: ignore
            raise PermissionDenied("You don't have permission")
        return post

    def get_serializer_class(self):
        return (
            serializers.PostListSerializer
            if self.action == "list"
            else serializers.PostSerializer
        )
