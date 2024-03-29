from base.paginations import DefaultPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from . import models, serializers

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
        model = models.Post
        fields = ["tags", "title", "created_from", "created_to", "author__username"]


class PostViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = models.Post.objects.none()
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
            queryset = models.Post.objects.filter(author=user)
        else:
            queryset = models.Post.objects.filter(publish_at__lt=timezone.now())
        return queryset.select_related("author").order_by("-id")

    def get_object(self):
        slug = self.kwargs[self.lookup_field]
        post = get_object_or_404(models.Post, slug=slug)
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


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "pk"
    queryset = models.Comment.objects.none()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = serializers.CommentSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        post_slug = self.kwargs.get("slug")
        return (
            models.Comment.objects.filter(post__slug=post_slug, parent=None)  # type: ignore
            .order_by("-id")
            .select_related("user")
            .prefetch_related("replies__user")
        )

    def get_object(self):
        id = self.kwargs[self.lookup_field]
        if not self.request.user:
            raise PermissionDenied("Invalid access")

        comment = get_object_or_404(models.Comment, id=id)
        if self.request.user.id != comment.user_id:  # type: ignore
            raise PermissionDenied("You don't have permission")
        return comment

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["post_slug"] = self.kwargs.get("slug")
        return context


class ReactionViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "pk"
    queryset = models.Comment.objects.none()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def create(self, request, *args, **kwargs):
        post_slug = kwargs.get("slug")
        post = get_object_or_404(models.Post, slug=post_slug)
        if models.Reaction.objects.filter(user=request.user, post=post).exists():
            raise ValidationError("You already react on this post")
        reaction = models.Reaction(user=request.user, post=post)
        reaction.save()
        return Response(
            status=status.HTTP_201_CREATED, data={"message": "Reaction added"}
        )

    @action(detail=False, methods=["delete"])
    def remove(self, request, *args, **kwargs):
        post_slug = kwargs.get("slug")
        post = get_object_or_404(models.Post, slug=post_slug)
        models.Reaction.objects.filter(user=request.user, post=post).delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT, data={"message": "Reaction removed"}
        )
