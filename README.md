# Ink & Signal

A small Flask blog with SQLite persistence, authentication, post CRUD, likes, comments, and notifications.

## Features

- **Authentication** — signup, login, and logout with hashed passwords. Users can log in with either username or email.
- **Posts** — create, read, edit, and delete posts. Users can only edit or delete their own posts.
- **Likes** — toggle likes on posts; liking a post sends a notification to the post author.
- **Comments** — comment on posts; commenting sends a notification to the post author.
- **Notifications** — per-user notification inbox (likes and comments), marked as read when viewed.
- **Database** — SQLite via Flask-SQLAlchemy, created automatically at `instance/blog.sqlite3` on first run.

## Tech stack

- [Flask](https://flask.palletsprojects.com/) 3.1.0 — web framework
- [Flask-Login](https://flask-login.readthedocs.io/) 0.6.3 — user session management
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) 3.1.1 — ORM and database abstraction
- [pytest](https://docs.pytest.org/) 8.3.4 — testing

## Project structure

```
flask-blog/
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── instance/               # SQLite database (created on first run)
├── app/
│   ├── __init__.py         # App factory, extensions, context processors
│   ├── models.py           # SQLAlchemy models (User, Post, Like, Comment, Notification)
│   ├── auth.py             # Auth blueprint (signup, login, logout)
│   ├── main.py             # Main blueprint (posts, likes, comments, notifications)
│   ├── static/
│   │   └── style.css       # Stylesheets
│   └── templates/
│       ├── base.html       # Base template
│       ├── index.html      # Post feed
│       ├── post_detail.html
│       ├── post_form.html
│       ├── notifications.html
│       └── auth/
│           ├── login.html
│       └── signup.html
└── tests/
    └── test_app.py         # Test suite
```

## Run locally

1. Clone the repository:

   ```powershell
   git clone <repo-url>
   cd flask-blog
   ```

2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Run the development server:

   ```powershell
   $env:FLASK_APP = "run.py"
   flask run --debug
   ```

5. Open http://127.0.0.1:5000 in your browser.

## Test

Run the test suite with pytest:

```powershell
pytest
```

Tests use a temporary SQLite database and cover signup, login, post CRUD, likes, comments, and notifications.

## Configuration

The SQLite database is created automatically at `instance/blog.sqlite3` on first run. Change `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI` through a production configuration before deployment.

Configuration keys used by the app factory:

| Key | Default | Description |
|-----|---------|-------------|
| `SECRET_KEY` | `dev-change-this-key` | Flask secret key for sessions and CSRF |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///blog.sqlite3` (instance-relative) | Database connection string |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Flask-SQLAlchemy modification tracking |
| `TESTING` | unset | Test mode flag |

## Routes

### Auth (`/auth`)

| Method | Path | Description | Auth required |
|--------|------|-------------|---------------|
| GET, POST | `/auth/signup` | Register a new account | No |
| GET, POST | `/auth/login` | Log in with username or email | No |
| POST | `/auth/logout` | Log out the current user | Yes |

### Posts

| Method | Path | Description | Auth required |
|--------|------|-------------|---------------|
| GET | `/` | List all posts, newest first | No |
| GET, POST | `/post/new` | Create a post | Yes |
| GET | `/post/<id>` | View a post and its comments/likes | No |
| GET, POST | `/post/<id>/edit` | Edit a post (author only) | Yes |
| POST | `/post/<id>/delete` | Delete a post (author only) | Yes |
| POST | `/post/<id>/like` | Toggle a like on a post | Yes |
| POST | `/post/<id>/comment` | Add a comment to a post | Yes |
| GET | `/notifications` | View and mark notifications as read | Yes |

## Database models

- **User** — `id`, `username`, `email`, `password_hash`; owns posts, comments, and likes.
- **Post** — `id`, `title`, `body`, `created_at`, `updated_at`, `user_id`; has comments and likes.
- **Like** — `id`, `user_id`, `post_id`, `created_at`; unique per user per post.
- **Comment** — `id`, `body`, `user_id`, `post_id`, `created_at`.
- **Notification** — `id`, `user_id`, `actor_id`, `post_id`, `kind`, `message`, `is_read`, `created_at`.

Passwords are hashed with Werkzeug's `generate_password_hash` / `check_password_hash`.

## License

This project is open source and available under the MIT License.
