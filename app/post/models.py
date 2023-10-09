from base.utils import create_slug
from django.contrib.auth import get_user_model
from django.db import models
from taggit.managers import TaggableManager

User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.CharField(blank=True)
    cover_image = models.ImageField(upload_to="posts", null=True)
    description = models.TextField()
    total_comment = models.PositiveIntegerField(default=0)
    total_reaction = models.PositiveIntegerField(default=0)

    publish_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    topics = TaggableManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = create_slug(Post, source_data=self.title, dest_field="slug")
        return super().save(*args, **kwargs)
