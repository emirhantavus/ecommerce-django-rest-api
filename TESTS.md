## 🧪 Automated Test Coverage

---

[![codecov](https://codecov.io/github/emirhantavus/ecommerce-django-rest-api/graph/badge.svg?token=XJ570NJD0O)](https://app.codecov.io/github/emirhantavus/ecommerce-django-rest-api/tree/main)

---

### 🛡 Authentication & User App

- **test_user_valid_login**
- **test_user_login_incorrect_password**
- **test_user_login_missing_password**
- **test_user_login_missing_email**
- **test_login_unregistered_email**
- **test_login_invalid_email_format**
- **test_request_password_reset_with_valid_email**
- **test_request_password_reset_with_invalid_email**
- **test_reset_password_with_valid_token**
- **test_reset_password_with_invalid_token**
- **test_login_with_old_password**
- **test_login_with_new_password**
- **test_user_registration**
- **test_missing_fields_registration**
- **test_empty_fields_registration**
- **test_weak_password_registration**
- **test_password_mismatch**
- **test_duplicate_email_registration**
- **test_password_hashing**

---

### 👤 Profile App

- **test_login**
- **test_get_profile**
- **test_update_profile**
- **test_unauthenticated_user_cannot_edit_profile**
- **test_user_cannot_edit_another_users_profile**

---

### 🏷️ Category App

- **test_add_category_admin**
- **test_add_category_not_admin**

---

### ⭐ Favorites App

- **test_add_favorite_item**
- **test_get_favorite_items**
- **test_control_get_favorite_items**
- **test_not_get_anothers_favorite_items**
- **test_delete_favorite_item**

---

### 🛒 Product App

- **test_add_product_authenticated**
- **test_add_product_unauthorizated**
- **test_add_product_authenticated_invalid**
- **test_delete_product_seller**
- **test_delete_product_customer**
- **test_delete_product_unauthenticated**
- **test_delete_product_seller_with_login**
- **test_delete_product_customer_with_login**
- **test_filter_by_seller**
- **test_filter_by_category**
- **test_filter_by_price**
- **test_filter_by_in_stock**
- **test_filter_by_not_in_stock**
- **test_filter_by_discounted**
- **test_product_search**
- **test_sort_by_created_at**
- **test_sort_by_stock**
- **test_get_all_products**
- **test_get_pk_product**
- **test_seller_can_update_product_put**
- **test_seller_can_update_product_patch**
- **test_customer_cannot_update_product**

---

### 🛒 Cart App

- **test_list_cart_without_authentication**
- **test_list_cart_empty_with_authentication**
- **test_add_to_cart**
- **test_delete_cart_item_without_authentication**
- **test_delete_cart_item_with_authentication**
- **test_add_to_cart**
- **test_cannot_add_product_with_zero_stock**
- **test_cannot_add_product_with_excess_quantity**

---

### 📦 Order App

- **test_customer_can_cancel_pending_order**
- **test_customer_cannot_cancel_others_order**
- **test_customer_cannot_cancel_non_pending_order**
- **test_unauth_user_cannot_cancel_order**
- **test_cancel_order_not_found**
- **test_cancel_returns_stock**
- **test_get_order_without_authenticate**
- **test_get_order_with_authenticate**
- **test_make_order**
- **test_cannot_create_order_when_cart_is_empty**
- **test_seller_can_list_own_product_return_requests**
- **test_seller_cannot_list_others_return_requests**
- **test_seller_can_approve_return_request**
- **test_seller_can_reject_return_request**
- **test_seller_cannot_process_another_sellers_request**
- **test_seller_cannot_process_non_requested_status**
- **test_unauthorized_user_cannot_process_return_request**
- **test_cannot_process_return_with_invalid_action**
- **test_return_request_not_found_returns_404**
- **test_customer_can_request_return_delivered_item**
- **test_customer_cannot_request_return_undelivered_item**
- **test_customer_cannot_request_return_twice**
- **test_customer_cannot_request_return_on_another_users_item**
- **test_unauthorized_user_cannot_request_return**
- **test_customer_can_list_own_return_requests**
- **test_seller_can_update_own_order_status**
- **test_seller_cannot_update_other_seller_status**
- **test_admin_can_update_any_order_status**
- **test_invalid_status_rejected**
- **test_order_not_found**
- **test_unauth_user_cannot_update_order**
- **test_update_order_status_cancelled**

---

### 💳 Payment App

- **test_payment_integration_success**
- **test_payment_creates_notifications**
- **test_payment_with_forbidden**
- **test_duplicate_transaction_id_fail**
- **test_payment_without_auth**
- **test_successful_payment**
- **test_invalid_id_payment**
- **test_double_payment_should_fail**
- **test_order_status_updated_after_successful_payment**
- **test_list_payments_no_auth**
- **test_list_payments_success**

---

### 🔔 Notification App

- **test_send_or_email_task_creates_notification**
- **test_send_notification_and_email_creates_notification**

---

### Admin Dashboard

- **test_admin_can_access_dashboard**
- **test_seller_cannot_access_admin_dashboard**
- **test_customer_cannot_access_admin_dashboard**
- **test_anonymous_user_cannot_access_admin_dashboard**
- **test_admin_dashboard_returns_correct_data**
- **test_admin_dashboard_with_no_data**
- **test_admin_dashboard_user_roles_counts**
- **test_admin_dashboard_invalid_method**
- **test_dashboard_wrong_role_access**

---

#### Seller Dashboard

- **test_seller_dashboard_with_valid_data**
- **test_seller_dashboard_requires_authentication**
- **test_customer_cannot_access_seller_dashboard**
- **test_seller_with_no_products_returns_zero**
- **test_seller_stock_alert_list_low_products**
- **test_seller_dashboard_calculates_sales_and_revenue**
- **test_seller_dashboard_response_contains_expected_fields**
- **test_seller_dashboard_with_pending_orders_only**
- **test_seller_dashboard_access_by_inactive_seller**