from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eDiary', '0005_signup_profileimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='signup',
            name='onboarding_done',
            field=models.BooleanField(default=False),
        ),
    ]
