# Library Management API

Django REST API for managing a library system with authentication, book inventory, borrowing and returning processes, and penalty tracking.

---

## Features

- JWT-based authentication (registration, login, token refresh)
- Book, author, and category management (admin only)
- Borrow and return system with:

  - Limit of 3 active borrows per user
  - Available copies tracking
  - Automatic due dates (14 days)
  - Atomic transactions for inventory updates
  - Late return penalty calculation

- PostgreSQL support for production

---

## Technology Stack

- Python 3.13
- Django & Django REST Framework
- `djangorestframework-simplejwt` for JWT auth
- PostgreSQL
- Poetry for dependency management

---

## Prerequisites

- Python 3.13+
- Poetry
- PostgreSQL database

---

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/library-management-api.git
cd library-management-api

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Update .env with production-ready values

# Apply migrations
poetry run python manage.py migrate

# Create superuser
poetry run python manage.py createsuperuser

# Collect static files
poetry run python manage.py collectstatic --noinput

# Run the server (development)
poetry run python manage.py runserver
```

---

## Environment Configuration

Example `.env` file:

```env
DJANGO_SECRET_KEY=replace-with-production-secret
DEBUG=False
DATABASE_URL=postgres://dbuser:dbpassword@dbhost:5432/library_db
ALLOWED_HOSTS=yourdomain.com
```

---

## API Endpoints

### Authentication

- `POST /api/register/` – Register
- `POST /api/login/` – Login
- `POST /api/token/refresh/` – Refresh token

### Books & Metadata

- `GET /api/books/` – List books (filterable)
- `GET /api/books/{id}/` – Book details
- `POST /api/books/` – Create (admin)
- `PUT /api/books/{id}/` – Update (admin)
- `DELETE /api/books/{id}/` – Delete (admin)
- `GET /api/authors/` / `POST /api/authors/` – Authors (admin)
- `GET /api/categories/` / `POST /api/categories/` – Categories (admin)

### Borrowing

- `POST /api/borrow/` – Borrow a book
- `GET /api/borrow/` – Active borrows for current user
- `POST /api/return/` – Return a book

### Penalties

- `GET /api/users/{id}/penalties/` – View penalty points (admin or self)

---

## Borrow and Return Logic

**Borrow**

1. Validate borrow limit
2. Lock book row for update
3. Check availability
4. Create borrow record (due date = borrow date + 14 days)
5. Decrement available copies

**Return**

1. Lock borrow and book rows
2. Set return date
3. Increment available copies
4. Calculate late days and apply penalties

---

## Deployment

- Set `DEBUG=False` in `.env`
- Set `ALLOWED_HOSTS` to your production domain
- Use PostgreSQL in production
- Serve static files via WhiteNoise or a dedicated static server
- Configure a WSGI server (Gunicorn, uWSGI) behind Nginx
