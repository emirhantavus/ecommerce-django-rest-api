## 🧪 Postman API Collections

Postman test collections and variables are available under the `/postman` directory.

- `Ecommerce_API_Collection.json`: Full API test scenarios (grouped by folder)

### 🔧 API Variables

The following variables are used throughout the Postman collection.  
They allow you to easily switch between local/dev/prod environments:

| Variable Name  | Example Value                      | Description                |
| -------------- | ---------------------------------- | -------------------------- |
| `base_url`     | `127.0.0.1:8000/api/`              | API base URL               |
| `user_url`     | `127.0.0.1:8000/api/users/`        | User endpoints             |
| `product_url`  | `127.0.0.1:8000/api/products/`     | Product endpoints          |
| `cart_url`     | `127.0.0.1:8000/api/cart/`         | Cart endpoints             |
| `order_url`    | `127.0.0.1:8000/api/order/`        | Order endpoints            |
| `payment_url`  | `127.0.0.1:8000/api/payment/`      | Payment endpoints          |

---

### 🚀 How to Use

1. **Download** the `.json` files from the `/postman` directory.
2. **Import** them into Postman using `Import > File`.
3. (Optional) **Review or adjust variables** as needed (see above).
4. Start testing the API endpoints instantly!