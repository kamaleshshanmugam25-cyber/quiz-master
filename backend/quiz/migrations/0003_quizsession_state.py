# Generated for persistent live quiz synchronization.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_alter_answerrecord_id_alter_choice_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizsession',
            name='state',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('question', 'Question'), ('leaderboard', 'Leaderboard'), ('ended', 'Ended'), ('answer_reveal', 'Answer reveal'), ('closed', 'Closed')], db_index=True, default='waiting', max_length=20),
        ),
        migrations.AddField(
            model_name='quizsession',
            name='current_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_sessions', to='quiz.question'),
        ),
        migrations.AddField(
            model_name='quizsession',
            name='timer_duration_seconds',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='quizsession',
            name='state_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quizsession',
            name='session_active',
            field=models.BooleanField(default=False),
        ),
    ]
