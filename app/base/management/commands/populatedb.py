import random
import multiprocessing
from uuid import uuid4

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from post.models import Comment, Post, Reaction
from base.utils import rand_str

fake = Faker()
User = get_user_model()

PROCESSORS = max(multiprocessing.cpu_count() - 2, 2)
WRITE_OPS_LIMIT = 10000

topics = (
    ["technology", "programming", "web development", "data science", "networking"]
    + ["food", "recipes", "cooking", "nutrition"]
    + ["travel", "adventure", "exploration", "vacation"]
    + ["sports", "fitness", "exercise", "health"]
    + ["music", "concerts", "festivals", "musicians"]
    + ["art", "painting", "sculpture", "creativity"]
)


def create_users(total_user):
    temp_user = User(username="username", full_name="name")
    temp_user.set_password(rand_str(20))
    password = temp_user.password

    user_ops = []
    for _ in range(total_user):
        user = fake.simple_profile()
        user_ops.append(
            User(username=uuid4().hex, full_name=user["name"], password=password)
        )

    User.objects.bulk_create(user_ops)

    print("User Created")


def create_posts(total_post):
    user_ids = list(User.objects.all().values_list("id", flat=True))
    for _ in range(total_post):
        description = fake.sentence(
            nb_words=random.randint(200, 1000), variable_nb_words=False
        )
        post = Post.objects.create(
            author_id=random.choice(user_ids),
            title=fake.name(),
            short_description=description[: random.randint(50, 200)],
            description=description,
            publish_at=timezone.now(),
        )
        post.topics.add(*random.sample(topics, random.randint(1, min(len(topics), 10))))
    print("Posts Created")


def create_reactions():
    user_ids = list(User.objects.all().values_list("id", flat=True))
    post_ids = list(Post.objects.all().values_list("id", flat=True))

    reaction_ops = []
    for post_id in post_ids:
        for user_id in random.sample(
            user_ids, random.randint(1, min(len(user_ids), 100))
        ):
            reaction_ops.append(Reaction(post_id=post_id, user_id=user_id))
    Reaction.objects.bulk_create(reaction_ops)
    print("Reaction Created")


def create_comments(total_comment=10):
    user_ids = list(User.objects.all().values_list("id", flat=True))
    post_ids = list(Post.objects.all().values_list("id", flat=True))
    comment_ops = []
    for _ in range(total_comment):
        comment_ops.append(
            Comment(
                post_id=random.choice(post_ids),
                user_id=random.choice(user_ids),
                description=fake.sentence(
                    nb_words=random.randint(20, 200), variable_nb_words=False
                ),
            )
        )
    Comment.objects.bulk_create(comment_ops)

    # Create Replies
    comment_ids = list(Comment.objects.all().values("id", "post_id"))
    total_reply = int(len(comment_ids) * 0.7)  # 70% comment will have reply

    reply_ops = []
    for comment in random.sample(comment_ids, total_reply):
        for _ in range(random.randint(1, 10)):
            """Comment will have 1 to 10 replies"""
            reply_ops.append(
                Comment(
                    parent_id=comment["id"],
                    post_id=comment["post_id"],
                    user_id=random.choice(user_ids),
                    description=fake.sentence(
                        nb_words=random.randint(20, 100), variable_nb_words=False
                    ),
                )
            )
    Comment.objects.bulk_create(reply_ops)
    print("Comments Created")


def populate_database(total_user=10, total_post=10):
    create_users(total_user)
    create_posts(total_post)

    create_reactions()
    create_comments()


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("--total_user", type=int)
        parser.add_argument("--total_post", type=int)

    def handle(self, *args, **options):
        total_user = options["total_user"]
        total_post = options["total_post"]

        populate_database(total_user=total_user, total_post=total_post)
