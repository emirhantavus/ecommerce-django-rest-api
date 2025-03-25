# 🚀 Ecommerce Django REST API Documentation

This document explains how to use the Ecommerce backend API built with **Django Rest Framework**.

---

## 📌 Authentication Endpoints

### 🔑 Register User

- **Endpoint:** `POST /api/register/`
- **Description:** Register a new user account.

**Request Body:**

```json
{
  "email": "user@gmail.com",
  "password": "securePass123",
  "password2": "securePass123",
  "phone_number": "5551234567"
}
```

**Response:**

```json
{
  "message": "User created successfully",
  "token": "YOUR_TOKEN"
}
```

---

### 🔐 Login User

- **Endpoint:** `POST /api/login/`
- **Description:** Authenticate user and obtain token.

**Request Body:**

```json
{
  "email": "user@gmail.com",
  "password": "securePass123"
}
```

**Response:**

```json
{
  "message": "Login successful.",
  "token": "YOUR_TOKEN"
}
```

---

### ✅ Check Token

- **Endpoint:** `GET /api/check-token/`
- **Description:** Check if token is valid and active.

**Headers:**

```
Authorization: Token YOUR_TOKEN
```

**Response:**

```json
{
  "user_id": 1,
  "is_valid": true
}
```

---

## 👤 User Profile Endpoints

### 🔍 Retrieve User Profile

- **Endpoint:** `GET /api/profile/{profile_id}/`
- **Description:** Retrieve profile details.

**Headers:**

```
Authorization: Token YOUR_TOKEN
```

**Response:**

```json
{
  "email": "user@gmail.com",
  "role": "seller",
  "seller_name": "John Doe",
  "company_name": "Doe Company"
}
```

---

### ✏️ Update User Profile

- **Endpoint:** `PUT /api/profile/{profile_id}/`
- **Description:** Update profile details.

**Headers:**

```
Authorization: Token YOUR_TOKEN
```

**Request Body (Partial update allowed):**

```json
{
  "seller_name": "New Seller Name",
  "company_name": "New Company LLC"
}
```

**Response:**

```json
{
  "email": "user@gmail.com",
  "role": "seller",
  "seller_name": "New Seller Name",
  "company_name": "New Company LLC"
}
```

---

### 🔒 Password Reset (Request)

- **Endpoint:** `POST /api/password-reset/`
- **Description:** Request password reset email.

**Request Body:**

```json
{
  "email": "user@gmail.com"
}
```

**Response:**

```json
{
  "message": "Password reset request received. Check your email"
}
```

---

### 🔑 Password Reset Confirm

- **Endpoint:** `POST /api/password-reset-confirm/`
- **Description:** Confirm password reset with token.

**Request Body:**

```json
{
  "email": "user@gmail.com",
  "token": "TOKEN_FROM_EMAIL",
  "new_password": "newpass123"
}
```

**Response:**

```json
{
  "message": "Password is changed successfully."
}
```

---

## 🛍 Product Endpoints

### 📦 List Products (with Filters)

- **Endpoint:** `GET /api/products/`
- **Description:** List products with optional filtering and sorting.

**Query Params:**
- `?search=phone`
- `?category=electronics`
- `?min_price=100&max_price=500`
- `?stock=1` (in stock products)
- `?discount=true`
- `?sort_by=price&order=asc`

**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "iPhone 14",
      "price": 999.99,
      "discount": true,
      "discounted_price": 899.99,
      "discount_rate": 10,
      "stock": 50,
      "active": true,
      "low_stock": {"low_stock": false},
      "category": 1,
      "is_favorited": true,
      "seller": {
        "id": 3,
        "email": "seller@gmail.com",
        "phone_number": "5551234567"
      }
    }
  ]
}
```

---

### 🔍 Product Detail

- **Endpoint:** `GET /api/products/{id}/`
- **Description:** Retrieve detailed product information.

---

## ⭐ Favorites Endpoints

### 🌟 List Favorites

- **Endpoint:** `GET /api/favorites/`
- **Description:** Retrieve user's favorite products.

### ➕ Add Product to Favorites

- **Endpoint:** `POST /api/favorites/`

**Request Body:**
```json
{
  "product_id": 1
}
```

### 🗑 Delete Favorite Product

- **Endpoint:** `DELETE /api/favorites/{favorite_id}/delete/`

---

## 📌 HTTP Status Codes & Error Handling

| Status Code | Meaning                                   |
|-------------|-------------------------------------------|
| `200`       | Success                                   |
| `201`       | Created successfully                      |
| `204`       | Deleted successfully                      |
| `400`       | Bad Request (validation errors, etc.)     |
| `401`       | Unauthorized (invalid/missing token)      |
| `403`       | Forbidden                                 |
| `404`       | Not Found                                 |
| `500`       | Internal Server Error                     |

---