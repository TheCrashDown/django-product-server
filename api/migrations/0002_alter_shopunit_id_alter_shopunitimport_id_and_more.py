# Generated by Django 4.0.6 on 2022-07-16 14:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopunit',
            name='id',
            field=models.UUIDField(default=uuid.UUID('661b6ed8-9b4e-4a18-8bdf-4c4c71931e1e'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='shopunitimport',
            name='id',
            field=models.UUIDField(default=uuid.UUID('e8d2d20b-ee38-4d9e-ad9a-9c96e50b1faf'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='shopunitstatisticresponse',
            name='id',
            field=models.UUIDField(default=uuid.UUID('18aa7867-6cfe-458b-a3c7-de3de84a1d25'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='shopunitstatisticunit',
            name='id',
            field=models.UUIDField(default=uuid.UUID('fb315162-4a05-4354-876d-d516a6932b6e'), editable=False),
        ),
        migrations.AlterField(
            model_name='shopunitstatisticunit',
            name='statid',
            field=models.UUIDField(default=uuid.UUID('aa1de8b6-a8f6-42b7-8e8a-0a735413366f'), editable=False, primary_key=True, serialize=False),
        ),
    ]
