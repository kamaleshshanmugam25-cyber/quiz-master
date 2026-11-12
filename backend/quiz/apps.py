from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    # Ensure unified groups: Admins + Participants
    admin_group, _ = Group.objects.get_or_create(name='Admins')

    # Remove legacy groups if they exist
    Group.objects.filter(name__in=['Teachers', 'Students']).delete()

    participants_group, _ = Group.objects.get_or_create(name='Participants')

    # Core quiz permissions
    quiz_perms = Permission.objects.filter(codename__in=[
        'add_quizset', 'change_quizset', 'delete_quizset', 'view_quizset',
        'add_question', 'change_question', 'delete_question', 'view_question',
        'view_quizsession', 'view_participant', 'change_participant',
    ])

    # Admins: full core perms
    admin_group.permissions.set(quiz_perms)

    # Participants: read-only to quiz content, limited to view
    participant_view_perms = Permission.objects.filter(codename__in=[
        'view_quizset', 'view_question', 'view_quizsession', 'view_participant'
    ])
    participants_group.permissions.set(participant_view_perms)


class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)

        # Guard Django's update_last_login signal to avoid pk=None update with djongo
        try:
            from django.contrib.auth.signals import user_logged_in
            from django.contrib.auth.models import update_last_login

            def safe_update_last_login(sender, user, **kwargs):
                try:
                    # Only attempt update if pk exists
                    if getattr(user, 'pk', None):
                        update_last_login(sender, user, **kwargs)
                except Exception:
                    # Best-effort: ignore failures so login can proceed
                    pass

            # Disconnect default handler then connect the safe one
            try:
                user_logged_in.disconnect(update_last_login)
            except Exception:
                pass
            user_logged_in.connect(safe_update_last_login)
        except Exception:
            # If anything goes wrong setting up the guard, continue without it
            pass