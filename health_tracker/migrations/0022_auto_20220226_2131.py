# Generated by Django 3.2.4 on 2022-02-26 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('health_tracker', '0021_auto_20220225_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='uploader',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploader', to='health_tracker.medworkerrep', verbose_name='Uploaded By'),
        ),
        migrations.CreateModel(
            name='HealthStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='patient', to='health_tracker.patients', verbose_name='Patient')),
            ],
        ),
    ]