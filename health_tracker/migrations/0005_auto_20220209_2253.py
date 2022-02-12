# Generated by Django 3.2.4 on 2022-02-09 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('health_tracker', '0004_auto_20220209_2239'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patients',
            name='user',
        ),
        migrations.AddField(
            model_name='patients',
            name='person',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='person', to=settings.AUTH_USER_MODEL),
        ),
    ]