# Generated by Django 3.1.7 on 2021-04-03 01:53

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210402_0315'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.reciepe_image_file_path),
        ),
    ]
