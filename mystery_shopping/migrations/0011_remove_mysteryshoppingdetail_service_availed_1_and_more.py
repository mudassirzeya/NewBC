# Generated by Django 4.2.2 on 2023-08-30 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "mystery_shopping",
            "0010_alter_mysteryshoppingoverview_service_agent_1_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mysteryshoppingdetail",
            name="service_availed_1",
        ),
        migrations.RemoveField(
            model_name="mysteryshoppingdetail",
            name="service_availed_2",
        ),
        migrations.RemoveField(
            model_name="mysteryshoppingdetail",
            name="service_availed_3",
        ),
        migrations.RemoveField(
            model_name="mysteryshoppingdetail",
            name="staff",
        ),
    ]