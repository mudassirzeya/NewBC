# Generated by Django 4.2.2 on 2023-08-29 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0009_remove_centralaccess_audit_and_more"),
        ("mystery_shopping", "0006_mysterychecklistpersonresponsible"),
    ]

    operations = [
        migrations.AddField(
            model_name="mysteryshoppingimages",
            name="staff",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="bc_app.userprofile",
            ),
        ),
    ]
