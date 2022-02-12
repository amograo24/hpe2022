# Generated by Django 3.2.4 on 2022-02-09 17:09

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('health_tracker', '0003_alter_user_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedWorkerRep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(default=None, max_length=100, null=True)),
                ('reg_no', models.CharField(default=None, max_length=20, verbose_name='Registration No./License ID')),
                ('hcwvid', models.CharField(default=None, max_length=10, unique=True, verbose_name='Health Care Worker/Vendor ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='aadharid',
        ),
        migrations.RemoveField(
            model_name='user',
            name='department',
        ),
        migrations.RemoveField(
            model_name='user',
            name='reg_no',
        ),
        migrations.RemoveField(
            model_name='user',
            name='wbid',
        ),
        migrations.AlterField(
            model_name='user',
            name='division',
            field=models.CharField(blank=True, choices=[('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'), ('I/SP', 'Insurance/Health Service Provider'), ('MSh', 'Medical Shop')], default=None, max_length=20, verbose_name='Division'),
        ),
        migrations.CreateModel(
            name='Patients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wbid', models.CharField(default=None, max_length=16, unique=True, validators=[django.core.validators.MinLengthValidator(12)], verbose_name='Well-Being ID')),
                ('aadharid', models.CharField(default=None, max_length=12, unique=True, validators=[django.core.validators.MinLengthValidator(12)], verbose_name='Aadhar ID')),
                ('hcw_v', models.ManyToManyField(blank=True, related_name='hcw_v', to='health_tracker.MedWorkerRep')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='medworkerrep',
            name='account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL),
        ),
    ]