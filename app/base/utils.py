from random import choice
from string import ascii_uppercase, digits

from django.utils.text import slugify


def rand_str(N=12):
    return "".join(choice(ascii_uppercase + digits) for _ in range(N))


def create_slug(model, source_data="None", dest_field="slug", filter_kwargs={}):
    slug = slugify(source_data, allow_unicode=True)
    count = model.objects.filter(
        **{f"{dest_field}__startswith": slug}, **filter_kwargs
    ).count()
    if count > 0:
        return f"{slug}-{count}-{rand_str(6)}"
    else:
        return slug
