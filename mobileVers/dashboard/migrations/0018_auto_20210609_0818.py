# Generated by Django 3.1.7 on 2021-06-09 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_auto_20210506_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='residencyform',
            name='document_title',
            field=models.CharField(choices=[('Identification', 'Identification'), ('Utility', 'Utility'), ('Free and Reduced Lunch', 'Free and Reduced Lunch')], max_length=30),
        ),
    ]
