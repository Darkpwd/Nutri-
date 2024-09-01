# Generated by Django 5.1 on 2024-08-30 01:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("plataforma", "0002_dadospacientes"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dadospacientes",
            old_name="colesterol_hdl",
            new_name="gordura",
        ),
        migrations.RenameField(
            model_name="dadospacientes",
            old_name="colesterol_ldl",
            new_name="hdl",
        ),
        migrations.RenameField(
            model_name="dadospacientes",
            old_name="percentual_gordura",
            new_name="ldl",
        ),
        migrations.RenameField(
            model_name="dadospacientes",
            old_name="percentual_musculo",
            new_name="musculo",
        ),
        migrations.RenameField(
            model_name="dadospacientes",
            old_name="trigliceridios",
            new_name="trigliceridos",
        ),
    ]
