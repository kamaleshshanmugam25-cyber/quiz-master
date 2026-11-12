import os
from pymongo import MongoClient

def main():
    uri = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017')
    dbname = os.getenv('MONGO_DB_NAME', 'quiz_db')
    client = MongoClient(uri)
    db = client[dbname]
    print('Connected to', uri, 'db:', dbname)
    cols = db.list_collection_names()
    for c in sorted(cols):
        try:
            cnt = db[c].count_documents({})
        except Exception:
            cnt = 'error'
        print(f"{c}: {cnt}")

if __name__ == '__main__':
    main()
