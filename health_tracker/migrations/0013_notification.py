# Generated by Django 3.2.5 on 2022-02-12 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health_tracker', '0012_alter_medworkerrep_hcwvid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=200, verbose_name="Sender's Name")),
                ('receiver', models.CharField(max_length=16, verbose_name="Receiver's Name")),
                ('content', models.CharField(max_length=200, verbose_name='Message Content')),
            ],
        ),
    ]