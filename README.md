[![CI](https://github.com/emirhantavus/ecommerce-django-rest-api/actions/workflows/ci.yaml/badge.svg)](https://github.com/emirhantavus/ecommerce-django-rest-api/actions)
[![codecov](https://codecov.io/github/emirhantavus/ecommerce-django-rest-api/graph/badge.svg?token=XJ570NJD0O)](https://app.codecov.io/github/emirhantavus/ecommerce-django-rest-api/tree/main)
![MIT License](https://img.shields.io/badge/license-MIT-green.svg)

# 🚀 Ecommerce Django REST API Project

A simple and modern backend for ecommerce projects, built with Django REST Framework.  
You can register, login, manage your profile, add products, make orders, and much more.  
Ready for both local development and production with Docker support.

---

## 🛠 Tech Stack

- Django, Django REST Framework
- PostgreSQL
- Redis (cache backend for fast API responses)
- Celery (background tasks)
- Docker & Docker Compose
- Flower (Celery dashboard)
- Python-dotenv
- Github Actions CI
- Django Silk (profiling & performance analysis in development)

---

## Folder Structure

```bash
.
├── backend/                # Django backend project
│   ├── ecommerce/          # Settings, celery, urls ...
│   ├── users/              # User app
│   ├── products/           # Product app
│   ├── cart/               # Cart app
│   ├── order/              # Order app
│   ├── payment/            # Payment app
│   ├── notifications/      # Notifications app
│   ├── manage.py
│   ├── requirements.txt
│
│
├── postman/                # Postman API collections
│   ├── Ecommerce_API_Collection.json
│   └── README.md
│
├── .env.example            # Example environment variables
├── docker-compose.yml      # Docker Compose file
├── Dockerfile              # Dockerfile for backend
└── README.md               # Project documentation

```

## 🌟 Features

- 🧩 **Modern Tech Stack:**  
  Django REST Framework, PostgreSQL, Docker & Docker Compose, Redis, Celery, Flower

- ⚡ **Async & Reliable:**  
  All emails (order, payment, shipment, cancel, etc.) are sent asynchronously via Celery & Redis

- ⚡ **Faster API Responses:**  
  Seller product APIs use Redis caching for better performance on repeated access. Caching can be extended to more endpoints in the future.

- 🛡 **Role-Based Access:**  
  Customer, seller, and admin roles with advanced permission management

- 🧪 **Test-Driven Development:**  
  High test coverage and clean code (TDD mindset)

- 🔁 **Continuous Integration:**  
  Automated tests run on every commit with GitHub Actions CI

- 📄 **API Documentation:**  
  Interactive API docs via Swagger, Redoc and Postman

- ⭐ **Favorites & Notifications:**  
  Save favorite products and get instant notifications for key events

- 🚀 **Production Ready:**  
  Easy .env configs, scalable setup, Dockerized environment

- 🛒 **Rich E-commerce Features:**  
  Advanced product filtering, order management, returns & refunds, order status updates, payment simulation

- 🔌 **Ready to Extend:**  
  Easily connect real email/SMS and payment services or scale to the cloud

--- 

## 📄 API Documentation

Interactive API documentation is available:

- **Swagger UI:**  
  [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Redoc:**  
  [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

You can explore and test all API endpoints directly from your browser

---

## 🧪 Postman Collection

All API tests and variables are in the [`/postman`](postman/) folder.
- Import [`Ecommerce_API_Collection.json`](postman/Ecommerce_API_Collection.json) to Postman and start testing.
- Detailed usage guide is inside the [`/postman/README.md`](postman/README.md).

---

## ⚡ Quick Start / Installation

```bash
# 1. Clone the repository
git clone https://github.com/emirhantavus/ecommerce-django-rest-api.git
cd ecommerce-django-rest-api

# 2. Create and activate virtualenv
python -m venv ecommerceenv

#For Windows:
ecommerceenv\Scripts\activate

#For Linux/macOS:
source ecommerceenv/bin/activate 

# 3. Install requirements
pip install -r requirements.txt

# 4. Migrate database
python manage.py migrate

# 5. Create a superuser (admin)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver

# 7. Run all tests
python manage.py test
```

---

## 🐳 Docker / Local Setup

To run the project with Docker:

```bash
# 1. Build and start all services (backend, db, redis, celery, flower)
docker-compose up --build

# 2. Go to the API:      http://localhost:8000/api/
# 3. Django admin:       http://localhost:8000/admin/
# 4. Flower dashboard:   http://localhost:5555/
# 5. Silk dashbooard:    http://localhost:8000/silk/
```

---

## ⚙️ Environment Variables

Main variables you need (.env or .env.docker)
You can use two .env files for docker and local development

Copy these to your ´.env´ or ´.env.docker´ file:

| Variable         | Description                        | Example         |
|------------------|------------------------------------|-----------------|
| SECRET_KEY       | Django secret key                  | your-secret-key |
| DJANGO_DB_NAME   | PostgreSQL database name           | ecommerce       |
| DJANGO_DB_USER   | PostgreSQL user                    | ecommerce       |
| DJANGO_DB_PASS   | PostgreSQL password                | ecommerce       |
| DJANGO_DB_HOST   | Database host (db for Docker)      | db              |
| DJANGO_DB_PORT   | Database port                      | 5432            |
| REDIS_HOST       | Redis host (for Celery & caching)  | redis           |
| REDIS_PORT       | Redis port                         | 6379            |

---

### 🧪 Automated Tests

See [TESTS.md](TESTS.md) for the full list of automated tests.

---

## 🚧 To-do / Missing Features

- Real payment gateway integration (like Stripe)  
  *(Currently, payment is only a simulation. Not required, but useful for production.)*

- SMTP email & SMS provider integration for production  
  *(Currently, all emails/notifications are printed to the console only.)*

- Order/Payment: PDF invoice and email receipt generation  
  *(Important for real-world use.)*

- Shipping and tracking API integration  
  *(Order status updates are manual now. Later, we can connect with a real shipping company API, or build a separate “logistics” app/microservice. This logistics app could be used for shipping in this project or even as a stand-alone logistics system.)*

- Seller: application/approval system and dashboard analytics  
  *(Now, there is no real application/approval for sellers and dashboard analytics are very basic.)*

- Admin: special API endpoints for bulk actions and advanced statistics  
  *(Not implemented yet.)*

- Security: API rate limiting, JWT token support (planned to switch from basic token), brute-force protection, advanced CORS configuration  
  *(Current version uses basic token auth. Security will be improved for production.)*

- Advanced cache invalidation or smarter cache strategies for product listing endpoints  
   *(Right now, only simple caching is used for seller products. In the future, more advanced caching can be added for better speed.)*

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

To contribute:
1. **Fork** this repository.
2. **Create a new branch** (`git checkout -b feature/my-feature`).
3. **Make your changes** and commit (`git commit -am 'Add new feature'`).
4. **Push to your fork** (`git push origin feature/my-feature`).
5. **Open a Pull Request** on GitHub.

For major changes, please open an issue first to discuss what you want to change.

> Feel free to open discussions or issues for any questions, ideas, or suggestions.

---

## 📝 License

See [LICENSE](LICENSE) for details.