# Generated by Django 4.1.7 on 2023-06-10 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0010_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
