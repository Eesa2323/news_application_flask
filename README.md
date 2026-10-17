# Ink & Signal

A Flask blog/news outlet with SQLite persistence, authentication, post CRUD, validation, likes, comments, and notifications.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_APP = "run.py"
flask run --debug
```

Open http://127.0.0.1:5000.

## Test

```powershell
pytest
```

The SQLite database is created automatically at `instance/blog.sqlite3` on first run. Change `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI` through a production configuration before deployment.
