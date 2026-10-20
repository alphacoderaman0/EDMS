from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eDiary', '0004_noteshistory_signup'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='profileImage',
            field=models.ImageField(blank=True, null=True, upload_to='profiles/'),
        ),
    ]
