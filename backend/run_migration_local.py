import os
from migrate_sql_to_mongo import main

def run():
    # default local MongoDB
    os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
    os.environ.setdefault('MONGO_DB_NAME', 'quiz_db')
    main()

if __name__ == '__main__':
    run()
