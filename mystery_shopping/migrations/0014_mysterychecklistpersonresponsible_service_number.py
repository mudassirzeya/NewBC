# Generated by Django 4.2.2 on 2023-08-30 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mystery_shopping", "0013_remove_mysteryshoppingdetail_center"),
    ]

    operations = [
        migrations.AddField(
            model_name="mysterychecklistpersonresponsible",
            name="service_number",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
