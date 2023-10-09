from datetime import timedelta

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
