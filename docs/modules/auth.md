# Auth Module

The `auth` module provides user authentication and access control for the log viewer.

## Table of Contents

- [Overview](#overview)
- [User Class](#user-class)
- [AuthManager Class](#authmanager-class)
- [Usage Examples](#usage-examples)

## Overview

The auth module provides:

- **User** - User account data class
- **AuthManager** - User authentication and session management
- **Role-based access** - viewer, analyst, admin roles
- **Session management** - Token-based sessions with expiration

## User Class

User account for log access.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `username` | `str` | required | Username |
| `password_hash` | `str` | required | Hashed password |
| `role` | `str` | `"viewer"` | User role |
| `created_at` | `datetime` | `now` | Account creation time |
| `last_login` | `Optional[datetime]` | `None` | Last login time |
| `active` | `bool` | `True` | Whether account is active |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_active` | `bool` | Check if user account is active |

### Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |
| `to_dict()` | Convert to dictionary |

## AuthManager Class

Manage user authentication and sessions.

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `ROLES` | `Dict[str, List[str]]` | Role permissions mapping |
| `SESSION_DURATION_HOURS` | `int` | Session duration (24 hours) |

### Constructor

```python
AuthManager(data_dir: str = "./data")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_dir` | `str` | `"./data"` | Data directory for user storage |

### Methods

#### create_user

```python
create_user(username: str, password: str, role: str = "viewer") -> bool
```

Create a new user.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | `str` | required | Username |
| `password` | `str` | required | Password (min 8 chars) |
| `role` | `str` | `"viewer"` | User role |

**Returns:** `bool` - True if created successfully

**Example:**

```python
auth = AuthManager()
success = auth.create_user("admin", "securepass123", role="admin")
```

#### authenticate

```python
authenticate(username: str, password: str) -> Optional[str]
```

Authenticate user and return session token.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | `str` | Username |
| `password` | `str` | Password |

**Returns:** `Optional[str]` - Session token or None

**Example:**

```python
token = auth.authenticate("admin", "securepass123")
if token:
    print(f"Authenticated: {token}")
```

#### validate_session

```python
validate_session(token: str) -> Optional[str]
```

Validate session token and return username.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | `str` | Session token |

**Returns:** `Optional[str]` - Username or None

**Example:**

```python
username = auth.validate_session(token)
if username:
    print(f"Valid session for: {username}")
```

#### check_permission

```python
check_permission(token: str, permission: str) -> bool
```

Check if user has a specific permission.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | `str` | Session token |
| `permission` | `str` | Permission to check |

**Returns:** `bool` - True if permitted

**Example:**

```python
if auth.check_permission(token, "manage"):
    print("User can manage")
```

#### has_permission

```python
has_permission(username: str, permission: str) -> bool
```

Check if a user has a specific permission by username.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | `str` | Username |
| `permission` | `str` | Permission to check |

**Returns:** `bool` - True if permitted

**Example:**

```python
if auth.has_permission("admin", "manage"):
    print("Admin can manage")
```

#### logout

```python
logout(token: str) -> None
```

Invalidate a session.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | `str` | Session token |

**Example:**

```python
auth.logout(token)
```

#### expire_sessions

```python
expire_sessions() -> int
```

Remove all expired sessions.

**Returns:** `int` - Number of expired sessions

**Example:**

```python
expired = auth.expire_sessions()
print(f"Expired {expired} sessions")
```

#### list_users

```python
list_users() -> List[Dict]
```

List all users (admin only).

**Returns:** `List[Dict]` - List of user dictionaries

**Example:**

```python
users = auth.list_users()
for user in users:
    print(f"{user['username']}: {user['role']}")
```

#### delete_user

```python
delete_user(username: str) -> bool
```

Delete a user.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | `str` | Username |

**Returns:** `bool` - True if deleted

**Example:**

```python
deleted = auth.delete_user("user1")
```

## Usage Examples

### Basic Setup

```python
from src.auth import AuthManager

auth = AuthManager(data_dir="./data")
```

### Create Users

```python
# Create admin
auth.create_user("admin", "securepass123", role="admin")

# Create analyst
auth.create_user("analyst", "analystpass123", role="analyst")

# Create viewer
auth.create_user("viewer", "viewerpass123", role="viewer")
```

### Authentication

```python
# Login
token = auth.authenticate("admin", "securepass123")
if token:
    print(f"Logged in: {token}")
else:
    print("Login failed")

# Validate session
username = auth.validate_session(token)
if username:
    print(f"Valid session for: {username}")

# Logout
auth.logout(token)
```

### Check Permissions

```python
# Check by token
if auth.check_permission(token, "manage"):
    print("User can manage")

# Check by username
if auth.has_permission("admin", "configure"):
    print("Admin can configure")
```

### Session Management

```python
# Expire old sessions
expired = auth.expire_sessions()
print(f"Expired {expired} sessions")
```

### List Users

```python
users = auth.list_users()
for user in users:
    print(f"{user['username']}: {user['role']}")
```

### Delete User

```python
deleted = auth.delete_user("user1")
if deleted:
    print("User deleted")
```

## Role Permissions

| Role | Permissions |
|------|-------------|
| `viewer` | read |
| `analyst` | read, search, export |
| `admin` | read, search, export, manage, configure |

## See Also

- [Web Dashboard](../dashboard.md) - Web interface authentication
