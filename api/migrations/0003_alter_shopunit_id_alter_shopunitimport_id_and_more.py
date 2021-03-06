# Generated by Django 4.0.6 on 2022-07-16 14:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_shopunit_id_alter_shopunitimport_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopunit',
            name='id',
            field=models.UUIDField(default=uuid.UUID('ca639fe8-7814-403c-bdb4-f50d1a9b35c0'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='shopunitimport',
            name='id',
            field=models.UUIDField(default=uuid.UUID('775e78a1-2640-4990-b8b3-11a90e3674e4'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='shopunitstatisticresponse',
            name='id',
            field=models.UUIDField(default=uuid.UUID('3211966f-a7dc-4899-bac9-bf751901e078'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='shopunitstatisticunit',
            name='id',
            field=models.UUIDField(default=uuid.UUID('e5389218-633e-4645-95f9-6d03738f18be'), editable=False),
        ),
        migrations.AlterField(
            model_name='shopunitstatisticunit',
            name='statid',
            field=models.UUIDField(default=uuid.UUID('9ef9554d-c8a3-40e2-b382-2bf5f3af1a44'), editable=False, primary_key=True, serialize=False),
        ),
    ]
