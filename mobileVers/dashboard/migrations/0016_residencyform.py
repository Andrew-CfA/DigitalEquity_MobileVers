# Generated by Django 3.1.7 on 2021-05-04 19:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0015_auto_20210427_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='residencyForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('document_title', models.CharField(choices=[('Identification', 'Identification'), ('Free and Reduced Lunch', 'Free and Reduced Lunch'), ('Utility', 'Utility')], max_length=30)),
                ('document', models.FileField(upload_to='')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserResidencyFiles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
