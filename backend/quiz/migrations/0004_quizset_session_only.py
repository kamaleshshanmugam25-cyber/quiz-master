from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_quizsession_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizset',
            name='session_only',
            field=models.BooleanField(default=False),
        ),
    ]
