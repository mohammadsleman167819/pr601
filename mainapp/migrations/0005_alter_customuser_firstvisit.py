# Generated by Django 5.0.3 on 2024-04-04 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_alter_customuser_firstvisit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='firstvisit',
            field=models.IntegerField(default=1),
        ),
    ]