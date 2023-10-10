from base.utils import create_slug
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
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

    def __str__(self) -> str:
        return f"{self.title[:32]}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = create_slug(Post, source_data=self.title, dest_field="slug")
        return super().save(*args, **kwargs)

    def handle_comment_count(self):
        self.total_comment = self.comments.count()  # type: ignore
        self.save()

    def handle_reaction_count(self):
        self.total_comment = self.reactions.count()  # type: ignore
        self.save()


class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "Comment", related_name="replies", on_delete=models.CASCADE, null=True
    )

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"post_id:{self.post_id} :: parent:{not self.parent_id} :: {self.description[:32]} "  # type: ignore


class Reaction(models.Model):
    user = models.ForeignKey(User, related_name="reactions", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="reactions", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.post_id} :: {self.user_id}"  # type: ignore


@receiver(post_save, sender=Comment)
def comment_post_save_receiver(sender, instance, created, **kwargs):
    if created:
        instance.post.handle_comment_count()


@receiver(post_delete, sender=Comment)
def comment_post_delete_receiver(sender, instance, **kwargs):
    instance.post.handle_comment_count()


@receiver(post_save, sender=Reaction)
def reaction_post_save_receiver(sender, instance, created, **kwargs):
    if created:
        instance.post.handle_comment_count()


@receiver(post_delete, sender=Reaction)
def reaction_post_delete_receiver(sender, instance, **kwargs):
    instance.post.handle_comment_count()
