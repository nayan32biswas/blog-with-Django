# Generated by Django 4.2.6 on 2023-10-08 15:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0003_alter_post_cover_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="cover_image",
            field=models.ImageField(null=True, upload_to="posts"),
        ),
    ]
