# Generated by Django 3.2.4 on 2022-02-10 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health_tracker', '0006_auto_20220210_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medworkerrep',
            name='department',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]