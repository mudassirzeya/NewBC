# Generated by Django 4.2.2 on 2023-08-30 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mystery_shopping", "0015_remove_mysteryshoppingimages_center"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mysteryshoppingdetail",
            name="remark",
        ),
        migrations.AddField(
            model_name="mysterychecklistpersonresponsible",
            name="remark",
            field=models.TextField(blank=True, null=True),
        ),
    ]
