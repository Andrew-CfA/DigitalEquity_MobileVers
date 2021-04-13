# Generated by Django 3.1.3 on 2021-03-22 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_zipcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='futureEmails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]