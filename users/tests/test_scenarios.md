# User Authentication & Profile Testing

## Test Scenarios

### 1.Registration
- Ensure a user can register with valid credentials.
- Validate password strength requirements.
- Test registration with missing fields. 
- Test registration with empty strings.
- Test registration with weak password.
- Test registration with duplicate email.
- Test password hashing.

### 2.Login
- Ensure a user can log in with valid credentials.
- Test login with incorrect password (should fail).
- Test login with missing fields.
- Test login with unregistered email.
- Test login with invalid email format.

### 3.Profile Management
- Ensure a user can edit their profile.
- Check that unauthorized users can not edit another user's profile.

### 4.Token Authentication
- Verify that a valid token can access to protected endpoints.
- Ensure an expired token deniess access.
- Test refreshing token.


## To-Do List
- [x] Test user registration
- [x] Test login func
- [x] Validate token authentication
- [ ] Test profile update func
- [ ] Check unauthorized profile access
- [ ] Ensure token refresh works correctly