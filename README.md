# ✦ Spark — Tinder-Style Dating App

A full-stack Django + MySQL dating application with real-time chat, profile photos, swipe-based matching, and separate user/admin interfaces.

---

## 📁 Project Structure

```
tinderapp/
├── manage.py
├── requirements.txt
├── tinderapp/              # Core config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py             # WebSocket (Channels)
│   └── wsgi.py
├── accounts/               # Custom User model, auth
├── profiles/               # Profile, photos, interests
├── matching/               # Swipes, matches logic
├── chat/                   # Real-time WebSocket chat + reports
├── admin_panel/            # Custom staff dashboard
├── templates/              # All HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── profiles/
│   ├── matching/
│   ├── chat/
│   └── admin_panel/
├── static/                 # CSS, JS, images
└── media/                  # Uploaded photos
```

---

## ⚙️ Prerequisites

| Tool    | Version  |
|---------|----------|
| Python  | 3.10+    |
| MySQL   | 8.0+     |
| Redis   | 6.0+     |

---

## 🚀 Setup Guide

### 1. Clone & Virtual Environment

```bash
git clone <your-repo>
cd tinderapp
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MySQL Database

```sql
-- In MySQL shell:
CREATE DATABASE tinderapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sparkuser'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON tinderapp_db.* TO 'sparkuser'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure Settings

Edit `tinderapp/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tinderapp_db',
        'USER': 'sparkuser',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Redis (for WebSocket chat)

```bash
# Ubuntu/Debian:
sudo apt install redis-server
sudo systemctl start redis

# macOS:
brew install redis && brew services start redis

# Windows: Use Redis via WSL2 or Docker
docker run -d -p 6379:6379 redis
```

### 5. Run Migrations

```bash
python manage.py makemigrations accounts profiles matching chat admin_panel
python manage.py migrate
```

### 6. Seed Interests

```bash
python manage.py seed_interests
```

### 7. Create Admin User

```bash
python manage.py createsuperuser
# Then in Django shell, make them admin:
python manage.py shell
>>> from accounts.models import User
>>> u = User.objects.get(email='your@email.com')
>>> u.is_admin = True
>>> u.save()
```

### 8. Start the Server

**Development (with WebSocket support):**
```bash
python manage.py runserver
```
For full WebSocket support use Daphne:
```bash
daphne -p 8000 tinderapp.asgi:application
```

---

## 🗃️ Database Schema

### MySQL Tables

| Table              | Description                          |
|--------------------|--------------------------------------|
| `users`            | Custom user model (email-based auth) |
| `profiles`         | Extended profile info, bio, gender   |
| `profile_photos`   | Multiple photos per profile          |
| `interests`        | Global interest tags                 |
| `profile_interests`| M2M: profiles ↔ interests            |
| `swipes`           | Like / dislike / superlike records   |
| `matches`          | Mutual likes = active match          |
| `messages`         | Chat messages between matched users  |
| `reports`          | User reports for moderation          |

---

## 🔑 Features

### User Side
- **Register / Login** — Email-based auth
- **Profile Setup** — Name, bio, birthday, gender, photos (up to 6), interests
- **Discover** — Card-stack swipe UI (drag or click buttons)
  - ❌ Dislike, ★ Super Like, ♥ Like
  - Animated LIKE / NOPE overlays
- **Match Detection** — Instant match modal on mutual like
- **Matches List** — All matches with last message preview + unread badge
- **Real-time Chat** — WebSocket-powered, typing indicators, read receipts
- **Report User** — In-chat report button with reason dropdown
- **Unmatch** — Remove a match from chat view

### Admin Side (`/admin-panel/`)
- **Dashboard** — Stats: total users, matches, messages, swipes, reports
- **User List** — Search, filter by status (active / banned / incomplete)
- **User Detail** — Full profile view, photos, matches, swipe stats, reports received
- **Ban / Unban** — One-click with confirmation
- **Verify Profile** — Toggle verification badge
- **Reports Queue** — Review, act on reports, ban from report view
- **Django Admin** — Full ORM admin at `/django-admin/`

---

## 🌐 URL Map

```
/                           → Redirect to /profiles/discover/
/accounts/register/         → Registration
/accounts/login/            → Login
/accounts/logout/           → Logout
/profiles/discover/         → Swipe deck
/profiles/edit/             → Edit profile + upload photos
/profiles/<id>/             → Public profile view
/matching/swipe/            → POST: swipe action (JSON API)
/matching/matches/          → Matches list
/chat/<user_id>/            → Chat room
/chat/report/<user_id>/     → POST: submit report
/admin-panel/               → Admin dashboard
/admin-panel/users/         → User management
/admin-panel/reports/       → Moderation queue
/django-admin/              → Django built-in admin
ws/chat/<user_id>/          → WebSocket chat endpoint
```

---

## 🏗️ Architecture Notes

- **WebSockets**: Django Channels + Redis channel layer. Chat uses room names like `chat_<smaller_id>_<larger_id>` to ensure both users join the same group.
- **Match Logic**: A `Swipe` record is created on every swipe. On a like/superlike, the system checks if the other user already liked back → creates a `Match`.
- **Auth**: Custom `User` model (`accounts.User`) with email as USERNAME_FIELD. Profiles are separate and linked 1:1.
- **Photo Storage**: Local filesystem via Django's `MEDIA_ROOT`. For production, swap `DEFAULT_FILE_STORAGE` to S3.
- **Interest Filtering**: Profiles filter by `interested_in` preference when building the discovery deck.

---

## 🛡️ Production Checklist

- [ ] Set `DEBUG = False` and `SECRET_KEY` via environment variable
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use `daphne` or `uvicorn` with ASGI for WebSocket support
- [ ] Set up Nginx as reverse proxy
- [ ] Move media storage to S3 (use `django-storages`)
- [ ] Add SSL/TLS (wss:// required for WebSocket in production)
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Configure proper email backend (SMTP/SendGrid)
- [ ] Set up database connection pooling (PgBouncer / ProxySQL)
- [ ] Add rate limiting to swipe and chat endpoints

---

## 📦 Tech Stack

| Layer       | Technology                     |
|-------------|-------------------------------|
| Backend     | Django 4.2                    |
| Database    | MySQL 8 + mysqlclient         |
| Real-time   | Django Channels + Redis       |
| Images      | Pillow + Django FileField     |
| Frontend    | Vanilla JS + CSS Variables    |
| Fonts       | Syne + DM Sans (Google Fonts) |
| WebServer   | Daphne (ASGI) / Gunicorn      |
