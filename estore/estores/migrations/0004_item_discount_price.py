# Generated by Django 4.0.3 on 2022-03-25 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estores', '0003_item_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='discount_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]