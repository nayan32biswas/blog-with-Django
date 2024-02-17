import multiprocessing
import random
from typing import List
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
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


def get_random_weighted_numbers(
    lo: int, hi: int, w_r_lo: int, w_r_hi: int, frequency=10
) -> List:
    """return a random range where frequency of weighted_range is higher"""
    weighted_numbers = frequency * list(range(w_r_lo, w_r_hi)) + list(range(lo, hi))
    random.shuffle(weighted_numbers)
    return weighted_numbers


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
            nb_words=random.randint(100, 500), variable_nb_words=False
        )
        post = Post.objects.create(
            author_id=random.choice(user_ids),
            title=fake.name(),
            short_description=description[: random.randint(10, 100)],
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


def create_comments():
    user_ids = list(User.objects.all().values_list("id", flat=True))
    post_ids = list(Post.objects.all().values_list("id", flat=True))
    weighted_numbers = get_random_weighted_numbers(
        lo=1, hi=50, w_r_lo=1, w_r_hi=5, frequency=100
    )

    comment_ops = []
    total_comment = int(len(post_ids) * 0.5)  # 50% post will have comment
    for post_id in random.sample(post_ids, total_comment):
        for _ in range(random.choice(weighted_numbers)):
            """Post will have 1 to 50 comments where frequency of 1 to 5 will be 100 time high"""
            comment_ops.append(
                Comment(
                    post_id=post_id,
                    user_id=random.choice(user_ids),
                    description=fake.sentence(
                        nb_words=random.randint(10, 50), variable_nb_words=False
                    ),
                )
            )
    Comment.objects.bulk_create(comment_ops)

    # Create Replies
    comment_ids = list(Comment.objects.all().values("id", "post_id"))
    total_reply = int(len(comment_ids) * 0.3)  # 30% comment will have reply

    reply_ops = []
    for comment in random.sample(comment_ids, total_reply):
        for _ in range(random.choice(weighted_numbers)):
            """Comment will have 1 to 50 replies where frequency of 1 to 5 will be 100 time high"""
            reply_ops.append(
                Comment(
                    parent_id=comment["id"],
                    post_id=comment["post_id"],
                    user_id=random.choice(user_ids),
                    description=fake.sentence(
                        nb_words=random.randint(5, 20), variable_nb_words=False
                    ),
                )
            )
    Comment.objects.bulk_create(reply_ops)
    print("Comments Created")


def update_relevant_fields():
    from django.db import connection

    update_total_comment_query = """
        UPDATE post_post SET total_comment = COALESCE((
            SELECT COUNT(*) FROM post_comment
            WHERE post_comment.post_id = post_post.id
            GROUP BY post_post.id
        ), 0);
    """
    update_total_reaction_query = """
        UPDATE post_post SET total_reaction = COALESCE((
            SELECT COUNT(*) FROM post_reaction
            WHERE post_reaction.post_id = post_post.id
            GROUP BY post_post.id
        ), 0);
    """

    with connection.cursor() as cursor:
        cursor.execute(update_total_comment_query)
        cursor.execute(update_total_reaction_query)


def populate_database(total_user=10, total_post=10):
    create_users(total_user)
    create_posts(total_post)

    create_reactions()
    create_comments()

    update_relevant_fields()


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("--total_user", type=int)
        parser.add_argument("--total_post", type=int)

    def handle(self, *args, **options):
        total_user = options["total_user"]
        total_post = options["total_post"]

        populate_database(total_user=total_user, total_post=total_post)
