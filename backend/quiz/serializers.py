from rest_framework import serializers
from .models import QuizSet, Question, Choice, QuizSession, SessionQuizSet, Participant


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'image']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'timer_seconds', 'order', 'choices', 'image']


class QuizSetSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = QuizSet
        fields = ['id', 'title', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quizset = super().create(validated_data)
        for q_data in questions_data:
            choices_data = q_data.pop('choices', [])
            question = Question.objects.create(quiz=quizset, **q_data)
            for c_data in choices_data:
                Choice.objects.create(question=question, **c_data)
        return quizset

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if 'questions' in validated_data:
            instance.questions.all().delete()
            for q_data in validated_data['questions']:
                choices_data = q_data.pop('choices')
                question = Question.objects.create(quiz=instance, **q_data)
                for c_data in choices_data:
                    Choice.objects.create(question=question, **c_data)

        return instance


class PlayerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'image']


class PlayerQuestionSerializer(serializers.ModelSerializer):
    choices = PlayerChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'timer_seconds', 'order', 'choices', 'image']


class PlayerQuizSetSerializer(serializers.ModelSerializer):
    questions = PlayerQuestionSerializer(many=True)

    class Meta:
        model = QuizSet
        fields = ['id', 'title', 'questions']


class SessionQuizSetSerializer(serializers.ModelSerializer):
    quiz_set = QuizSetSerializer(read_only=True)
    # Use PrimaryKeyRelatedField for write operations (correct FK handling)
    quiz_set_id = serializers.PrimaryKeyRelatedField(
        queryset=QuizSet.objects.all(),
        source='quiz_set',
        write_only=True,
        required=False,
    )

    class Meta:
        model = SessionQuizSet
        fields = ['id', 'quiz_set', 'quiz_set_id', 'order', 'completed', 'added_at']


class ParticipantSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    avatar_svg = serializers.SerializerMethodField()
    total_attended = serializers.SerializerMethodField()
    correct_count = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = [
            'id', 'username', 'joined_at', 'score', 'total_response_time',
            'avatar_id', 'avatar_url', 'avatar_svg',
            'total_attended', 'correct_count', 'accuracy',
        ]

    def get_avatar_url(self, obj):
        return obj.avatar_url or None

    def get_avatar_svg(self, obj):
        return None

    def get_total_attended(self, obj):
        if hasattr(obj, 'annotated_attended'):
            return obj.annotated_attended
        return obj.answers.count()

    def get_correct_count(self, obj):
        if hasattr(obj, 'annotated_correct'):
            return obj.annotated_correct
        return obj.answers.filter(correct=True).count()

    def get_accuracy(self, obj):
        attended = getattr(obj, 'annotated_attended', None)
        if attended is None:
            attended = obj.answers.count()
        if attended == 0:
            return 0
        correct = getattr(obj, 'annotated_correct', None)
        if correct is None:
            correct = obj.answers.filter(correct=True).count()
        return round((correct / attended) * 100)


class QuizSessionSerializer(serializers.ModelSerializer):
    quiz_sets = SessionQuizSetSerializer(many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    current_quiz_set = QuizSetSerializer(read_only=True)

    class Meta:
        model = QuizSession
        fields = [
            'id', 'code', 'host', 'created_at', 'started', 'finished',
            'current_quiz_set', 'current_question_index', 'state',
            'current_question', 'timer_duration_seconds', 'session_active',
            'quiz_sets', 'participants',
        ]



class PlayerSessionQuizSetSerializer(serializers.ModelSerializer):
    quiz_set = PlayerQuizSetSerializer(read_only=True)

    class Meta:
        model = SessionQuizSet
        fields = ['id', 'quiz_set', 'order', 'completed', 'added_at']


class PlayerQuizSessionSerializer(serializers.ModelSerializer):
    quiz_sets = PlayerSessionQuizSetSerializer(many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    current_quiz_set = PlayerQuizSetSerializer(read_only=True)

    class Meta:
        model = QuizSession
        fields = [
            'id', 'code', 'host', 'created_at', 'started', 'finished',
            'current_quiz_set', 'current_question_index', 'state',
            'current_question', 'timer_duration_seconds', 'session_active',
            'quiz_sets', 'participants',
        ]
