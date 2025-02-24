# Generated by Django 5.0 on 2024-09-15 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0002_event"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="event",
            name="image",
        ),
        migrations.AddField(
            model_name="event",
            name="image_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="event_date",
            field=models.DateField(),
        ),
    ]
