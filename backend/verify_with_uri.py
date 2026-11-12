import os
import sys
from verify_mongo import main

def run():
    # Require MONGO_URI from environment to avoid embedding credentials
    if not os.getenv('MONGO_URI'):
        print('MONGO_URI not set. Please set it in environment and re-run.')
        sys.exit(1)
    main()

if __name__ == '__main__':
    run()
