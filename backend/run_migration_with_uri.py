import os
import sys
from migrate_sql_to_mongo import main

def run():
    # This runner intentionally does NOT embed credentials.
    # Set MONGO_URI and MONGO_DB_NAME in your environment before running.
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print('MONGO_URI not set. Aborting to avoid embedding credentials in repo.')
        sys.exit(1)
    print('Using MONGO_URI from environment (redacted)')
    main()

if __name__ == '__main__':
    run()
