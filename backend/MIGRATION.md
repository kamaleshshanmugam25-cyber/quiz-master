Migration guide: SQLite -> MongoDB

Overview
--------
This project ships with a simple helper script `migrate_sql_to_mongo.py` that copies rows from the local `db.sqlite3` into a MongoDB database (one SQLite table -> one MongoDB collection). The Django settings have been updated to support using MongoDB (via `djongo`) when a Mongo URI is provided.

Summary of changes made
- `backend/backend/settings.py`: now uses `MONGO_URI` (or `DATABASE_URL`) if present and falls back to local `db.sqlite3` otherwise.
- `backend/migrate_sql_to_mongo.py`: made portable (uses project `db.sqlite3` by default), respects `SQLITE_PATH`, `MONGO_URI`, and `MONGO_DB_NAME`, skips internal sqlite tables, and bulk-inserts documents.

Pre-migration checklist
----------------------
1. Backup your SQLite DB:

   Open a command prompt in the `backend` folder and run:
   ```cmd
   copy db.sqlite3 db.sqlite3.bak
   ```

2. Ensure you have a MongoDB instance available:
   - Local: install MongoDB and ensure `mongod` is running on `127.0.0.1:27017`.
   - Atlas: create a free cluster and obtain the connection string.

3. Install Python dependencies (prefer a venv):
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Use a `.env` file for secrets (recommended)

   - Copy the example file and fill it locally (do NOT commit `.env`):

     ```cmd
     copy .env.example .env
     ```

   - Edit `.env` and set `MONGO_URI`, `MONGO_DB_NAME`, and any other secrets.
   - The backend repo already contains a `.gitignore` entry to ignore `.env`.

Running the migration
---------------------
1. From the `backend` directory, set the Mongo connection environment variables.

   You can either set env vars directly or use a local `.env` file. Examples (cmd.exe):

   Directly:
   ```cmd
   set MONGO_URI=mongodb://127.0.0.1:27017
   set MONGO_DB_NAME=quiz_db
   ```

   Or create a `.env` from the example and edit it:
   ```cmd
   copy .env.example .env
   rem (edit .env in your editor and set MONGO_URI)
   ```

   If you prefer Atlas, set `MONGO_URI` to your Atlas connection string (keep credentials secret). Example (Atlas SRV):
   ```cmd
   set MONGO_URI=mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority
   set MONGO_DB_NAME=quiz_db
   ```

2. Run the migration script:

   ```cmd
   python migrate_sql_to_mongo.py
   ```

3. Verify data in MongoDB using `mongo` shell, MongoDB Compass, or your Atlas UI.

Switching Django to MongoDB (optional)
-------------------------------------
If you want Django to use MongoDB (so the app reads/writes Mongo directly), set `MONGO_URI` (or `DATABASE_URL`) and optionally `MONGO_DB_NAME` before starting Django. Example (Windows cmd):

```cmd
set MONGO_URI=mongodb+srv://user:pass@cluster0.example.mongodb.net/?retryWrites=true&w=majority
set MONGO_DB_NAME=quiz-master
python manage.py runserver
```

Notes and caveats
-----------------
- The project currently uses `djongo` to allow Django ORM to talk to MongoDB. djongo may have compatibility limitations depending on Django version. Test thoroughly.
- If you prefer not to use `djongo`, consider using `pymongo` or `mongoengine` and porting data-access code in the app—this is a larger change.
- Keep the SQLite backup (`db.sqlite3.bak`) until you're satisfied with Mongo data.

Rollback
--------
- If something goes wrong, restore the SQLite backup:

```cmd
copy /Y db.sqlite3.bak db.sqlite3
```

Questions / Next steps
----------------------
- Do you want me to:
  - Run the migration here (I can't run it against your local DB but I can run it in the workspace if you provide access to the DB file),
  - Or change the project to fully use MongoDB (convert models to a document ODM like `mongoengine`),
  - Or only provide CI/production deployment guidance for Atlas?

If you'd like, I can also add a small verification script that connects to Mongo and prints a few collection counts.
