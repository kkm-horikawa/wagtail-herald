from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wagtail_herald", "0006_seosettings_ads_txt_security_txt"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="seosettings",
            name="title_separator",
        ),
    ]
