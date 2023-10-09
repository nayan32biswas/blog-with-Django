from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField
from user.serializers import UserMinimalSerializer

from . import models


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    topics = TagListSerializerField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author_profile = UserMinimalSerializer(read_only=True, source="author")

    class Meta:
        model = models.Post
        fields = [
            "topics",
            "title",
            "slug",
            "description",
            "short_description",
            "publish_at",
            "cover_image",
            "author",
            "author_profile",
            "total_comment",
            "total_reaction",
        ]
        extra_kwargs = {
            "slug": {"read_only": True},
            "total_comment": {"read_only": True},
            "total_reaction": {"read_only": True},
        }

    def validate(self, attrs):
        publish_at = attrs.get("publish_at")
        if publish_at and publish_at < (timezone.now() - timedelta(minutes=10)):
            """
            Make sure publish_at is getter than current time
            timedelta(minutes=10) is for offset between
                user requested time and server current time
            """
            raise serializers.ValidationError(_("Invalid Publish at"))
        return super().validate(attrs)


class PostListSerializer(TaggitSerializer, serializers.ModelSerializer):
    author_profile = UserMinimalSerializer(read_only=True, source="author")

    class Meta:
        model = models.Post
        fields = [
            "title",
            "short_description",
            "slug",
            "author_profile",
            "total_comment",
            "total_reaction",
        ]


class ReplySerializer(serializers.ModelSerializer):
    user_profile = UserMinimalSerializer(read_only=True, source="user")

    class Meta:
        model = models.Comment
        fields = [
            "id",
            "description",
            "user_profile",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_profile = UserMinimalSerializer(read_only=True, source="user")
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = models.Comment
        fields = [
            "id",
            "description",
            "parent",
            "user",
            "user_profile",
            "replies",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "parent": {"write_only": True},
        }

    def validate(self, attrs):
        parent = attrs.get("parent")
        post = get_object_or_404(models.Post, slug=self.context.get("post_slug"))
        if parent:
            if parent.parent_id:
                raise serializers.ValidationError(
                    _("Multi level nesting is not supported")
                )
            if post.id != parent.post_id:
                raise serializers.ValidationError(
                    _("Post is not valid for parent comment")
                )

        attrs["post"] = post
        return super().validate(attrs)
