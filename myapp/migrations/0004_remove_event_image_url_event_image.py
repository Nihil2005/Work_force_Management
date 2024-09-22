# Generated by Django 5.0 on 2024-09-15 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_remove_event_created_at_remove_event_image_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="image_url",
        ),
        migrations.AddField(
            model_name="event",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="event_images/"),
        ),
    ]
