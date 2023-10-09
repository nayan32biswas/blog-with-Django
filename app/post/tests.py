from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from . import models

User = get_user_model()


USER_DATA = {
    "username": "demousername",
    "password": "demopassword",
    "full_name": "User Name",
}
POST_DATA = {
    "title": "Test Post",
    "publish_at": timezone.now(),
    "short_description": "Short Description",
    "description": "Long Description, Long Description, Long Description, Long Description, Long Description, Long Description",
    "cover_image": None,
    "topics": ["one", "two"],
}
COMMENT_DATA = {"description": "Comment Content"}


class PostTestCase(TestCase):
    def setUp(self):
        self.base_user = User.objects.create_user(**USER_DATA)  # type: ignore

        self.post_url = "/api/v1/posts/"
        self.client: Any = APIClient()

    def create_post(self):
        post = models.Post(**POST_DATA, author=self.base_user)
        post.save()
        return post

    def test_create_post(self):
        payload = {**POST_DATA}
        self.client.force_authenticate(user=self.base_user)
        response = self.client.post(self.post_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_posts(self):
        response = self.client.get(self.post_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_posts(self):
        self.client.force_authenticate(user=self.base_user)
        response = self.client.get(
            self.post_url,
            params={"author__username": self.base_user.username},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_details(self):
        post = self.create_post()
        url = f"{self.post_url}{post.slug}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_unpublished_post_details(self):
        """
        Check if user can get post that are not published.
        Also check if author can get the post.
        """
        post = self.create_post()
        post.publish_at = timezone.now() + timedelta(days=1)
        post.save()

        url = f"{self.post_url}{post.slug}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.base_user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post(self):
        post = self.create_post()
        url = f"{self.post_url}{post.slug}/"
        update_title = POST_DATA["title"] + " update"

        self.client.force_authenticate(user=self.base_user)
        response = self.client.patch(url, data={"title": update_title}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(res_data["title"], update_title)

        post.refresh_from_db()
        self.assertEqual(post.title, update_title)

    def test_delete_post(self):
        post = self.create_post()
        url = f"{self.post_url}{post.slug}/"

        self.client.force_authenticate(user=self.base_user)
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentTestCase(TestCase):
    def setUp(self):
        self.base_user = User.objects.create_user(**USER_DATA)  # type: ignore

        post = models.Post(**POST_DATA, author=self.base_user)
        post.save()

        self.post = post
        self.comment_url = f"/api/v1/posts/{post.slug}/comments/"
        self.client: Any = APIClient()

    def create_comment(self):
        comment = models.Comment(**COMMENT_DATA, post=self.post, user=self.base_user)
        comment.save()
        return comment

    def create_reply(self):
        comment = self.create_comment()
        reply = models.Comment(
            **COMMENT_DATA, post=self.post, user=self.base_user, parent=comment
        )
        reply.save()
        return reply

    def test_create_comment(self):
        payload = {**COMMENT_DATA}
        self.client.force_authenticate(user=self.base_user)
        response = self.client.post(self.comment_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_post_comments(self):
        response = self.client.get(self.comment_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment(self):
        comment = self.create_comment()
        url = f"{self.comment_url}{comment.id}/"

        updated_description = "New description"
        self.client.force_authenticate(user=self.base_user)
        response = self.client.patch(
            url, data={"description": updated_description}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(res_data["description"], updated_description)

        comment.refresh_from_db()
        self.assertEqual(comment.description, updated_description)

    def test_delete_comment(self):
        comment = self.create_comment()
        url = f"{self.comment_url}{comment.id}/"

        self.client.force_authenticate(user=self.base_user)
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_reply(self):
        comment = self.create_comment()
        payload = {**COMMENT_DATA, "parent": comment.id}

        self.client.force_authenticate(user=self.base_user)
        response = self.client.post(self.comment_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_reply(self):
        reply = self.create_reply()
        url = f"{self.comment_url}{reply.id}/"

        updated_description = "New description"
        self.client.force_authenticate(user=self.base_user)
        response = self.client.patch(
            url, data={"description": updated_description}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(res_data["description"], updated_description)

        reply.refresh_from_db()
        self.assertEqual(reply.description, updated_description)

    def test_delete_reply(self):
        reply = self.create_reply()
        url = f"{self.comment_url}{reply.id}/"

        self.client.force_authenticate(user=self.base_user)
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
