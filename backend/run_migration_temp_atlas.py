import os
import sys
from migrate_sql_to_mongo import main

def run():
    # Do not embed credentials in repo. Require MONGO_URI from environment.
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print('MONGO_URI not set. Aborting to avoid embedding credentials in repo.')
        sys.exit(1)
    os.environ.setdefault('MONGO_DB_NAME', 'quiz_db')
    main()

if __name__ == '__main__':
    run()
