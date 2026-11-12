from pymongo import MongoClient

def verify_connection():
    # Connect to MongoDB
    uri = 'mongodb+srv://ansaris_db_user:gs1rqg7uOftUENW4@cluster0.ruuy9ps.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    client = MongoClient(uri)
    
    try:
        # Try to access the database
        db = client['quiz-master']
        
        # List all collections
        collections = db.list_collection_names()
        print("Successfully connected to MongoDB!")
        print("\nAvailable collections:")
        for collection in collections:
            # Get count of documents in each collection
            count = db[collection].count_documents({})
            print(f"- {collection}: {count} documents")
            
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False
    finally:
        client.close()

if __name__ == '__main__':
    verify_connection()