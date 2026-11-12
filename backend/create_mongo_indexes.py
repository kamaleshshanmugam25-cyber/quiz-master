import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import OperationFailure

def create_index_safely(collection, index_spec, **kwargs):
    """Create an index if it doesn't exist, ignoring if it does."""
    try:
        collection.create_index(index_spec, **kwargs)
        print(f'Created index on {collection.name}: {index_spec}')
    except OperationFailure as e:
        if 'Index already exists' in str(e):
            print(f'Index already exists on {collection.name}: {index_spec}')
        else:
            print(f'Error creating index on {collection.name}: {e}')
            raise

def create_indexes(mongo_uri=None, db_name=None):
    """Create recommended indexes for the quiz app collections."""
    # Use env vars or supplied arguments
    uri = mongo_uri or os.getenv('MONGO_URI')
    if not uri:
        print('MONGO_URI not set. Please set it in environment or pass as argument.')
        sys.exit(1)
    
    dbname = db_name or os.getenv('MONGO_DB_NAME', 'quiz_master')
    client = MongoClient(uri)
    db = client[dbname]
    print(f'Connected to MongoDB database {dbname}')

    # Quiz session indexes (lookup by code, host relationships)
    create_index_safely(db.quiz_quizsession, [('code', ASCENDING)], unique=True)
    create_index_safely(db.quiz_quizsession, [('host_id', ASCENDING)])
    create_index_safely(db.quiz_quizsession, [('created_at', DESCENDING)])  # Recent sessions

    # Participant indexes (session lookup, username uniqueness per session)
    create_index_safely(db.quiz_participant, [
        ('session_id', ASCENDING),
        ('username', ASCENDING)
    ], unique=True)
    create_index_safely(db.quiz_participant, [('user_id', ASCENDING)])

    # Answer record indexes (participant answers, question stats)
    create_index_safely(db.quiz_answerrecord, [('participant_id', ASCENDING)])
    create_index_safely(db.quiz_answerrecord, [('question_id', ASCENDING)])
    create_index_safely(db.quiz_answerrecord, [
        ('session_id', ASCENDING),
        ('question_id', ASCENDING)
    ])

    # Quiz questions and choices (quiz set relationship)
    create_index_safely(db.quiz_question, [('quiz_set_id', ASCENDING)])
    create_index_safely(db.quiz_question, [('order', ASCENDING)])  # Question order
    create_index_safely(db.quiz_choice, [('question_id', ASCENDING)])

    # Quiz set indexes (creator lookup, active status)
    create_index_safely(db.quiz_quizset, [('creator_id', ASCENDING)])
    create_index_safely(db.quiz_quizset, [('is_active', ASCENDING)])

    # Session-QuizSet relationship (session content)
    create_index_safely(db.quiz_sessionquizset, [
        ('session_id', ASCENDING),
        ('order', ASCENDING)
    ])

    # Auth/User indexes (common queries)
    create_index_safely(db.quiz_user, [('username', ASCENDING)], unique=True)
    create_index_safely(db.quiz_user, [('email', ASCENDING)], unique=True)
    create_index_safely(db.authtoken_token, [('user_id', ASCENDING)], unique=True)

    # Session/admin log indexes
    create_index_safely(db.django_session, [('expire_date', ASCENDING)])
    create_index_safely(db.django_admin_log, [
        ('user_id', ASCENDING),
        ('action_time', DESCENDING)
    ])

    print('\nIndex creation completed.')

if __name__ == '__main__':
    create_indexes()