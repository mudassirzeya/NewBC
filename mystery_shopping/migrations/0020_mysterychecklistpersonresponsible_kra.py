# Generated by Django 4.2.2 on 2023-09-11 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "mystery_shopping",
            "0019_remove_mysterychecklistpersonresponsible_service_number_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="mysterychecklistpersonresponsible",
            name="kra",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
