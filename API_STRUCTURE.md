# Trello Lite REST API Structure

## Overview
This project follows a RESTful architecture. All endpoints adhere to REST standards and conventions.

## Base URL
```
https://your-domain.com/api/v1/
```

## API Resources

### 1. Authentication (`/auth/`)
Authentication resources are separate from user management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register a new user |
| POST | `/auth/login/` | Login (obtain JWT tokens) |
| POST | `/auth/refresh/` | Refresh access token |
| POST | `/auth/logout/` | Logout |
| POST | `/auth/password/reset/` | Request password reset |
| POST | `/auth/password/reset/confirm/` | Confirm password reset |
| POST | `/auth/verify-email/` | Verify email address |

### 2. Users (`/users/`)
User management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | List users (admin only) |
| GET | `/users/me/` | Current user info |
| GET | `/users/{id}/` | Specific user info |
| PATCH | `/users/me/` | Update current user |
| PATCH | `/users/{id}/` | Update specific user (admin) |
| DELETE | `/users/{id}/` | Delete user |
| POST | `/users/me/password/` | Change current user's password |
| POST | `/users/{id}/password/` | Change a user's password |

### 3. Profiles (`/profiles/`)
Manage user profiles as an independent resource.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profiles/` | List profiles |
| GET | `/profiles/me/` | Current user's profile |
| GET | `/profiles/{id}/` | Specific user's profile |
| PATCH | `/profiles/me/` | Update current user's profile |
| PATCH | `/profiles/{id}/` | Update specific user's profile |

### 4. Boards (`/boards/`)
Boards and related resources.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/` | List user boards |
| POST | `/boards/` | Create a new board |
| GET | `/boards/{id}/` | Board details |
| PATCH | `/boards/{id}/` | Update a board |
| DELETE | `/boards/{id}/` | Delete a board |
| GET | `/boards/public/` | List public boards |

#### Nested Resources - Members
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/{board_id}/members/` | List board members |
| DELETE | `/boards/{board_id}/members/{user_id}/` | Remove a member from board |

#### Nested Resources - Invitations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/{board_id}/invitations/` | List board invitations |
| POST | `/boards/{board_id}/invitations/` | Send a new invitation |
| POST | `/boards/{board_id}/invitations/user/` | Invite a registered user |

#### Board Actions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/boards/{board_id}/leave/` | Leave board |
| GET | `/boards/{board_id}/activities/` | Board activity history |

#### Nested Resources - Lists
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/{board_id}/lists/` | Board lists |
| POST | `/boards/{board_id}/lists/` | Create a new list |

### 5. Lists (`/lists/`)
List management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/lists/{id}/` | List details |
| PATCH | `/lists/{id}/` | Update list |
| DELETE | `/lists/{id}/` | Delete list |
| POST | `/lists/{id}/move/` | Move list to new position |

### 6. Tasks (`/tasks/`)
Task management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/` | Tasks assigned to current user |
| GET | `/tasks/{id}/` | Task details |
| PATCH | `/tasks/{id}/` | Update task |
| DELETE | `/tasks/{id}/` | Delete task |
| POST | `/tasks/{id}/move/` | Move task |
| POST | `/tasks/{id}/toggle-complete/` | Quick toggle completion status |

#### Nested Resources - Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/{task_id}/comments/` | List comments |
| POST | `/tasks/{task_id}/comments/` | Create a new comment |
| GET | `/tasks/{task_id}/comments/{id}/` | Comment details |
| PATCH | `/tasks/{task_id}/comments/{id}/` | Update comment |
| DELETE | `/tasks/{task_id}/comments/{id}/` | Delete comment |

#### List-specific Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/lists/{list_id}/` | Tasks of a list |
| POST | `/tasks/lists/{list_id}/` | Create a task in a list |

### 7. Invitations (`/invitations/`)
Manage user invitations.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/invitations/` | Current user's invitations |
| GET | `/invitations/{id}/` | Invitation details |
| POST | `/invitations/{id}/respond/` | Respond to invitation (accept/reject) |

### 8. User Limits (`/limits/`)
User limits.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/limits/` | Limits for current user |
| GET | `/limits/{user_id}/` | Limits for a specific user (admin) |

## REST Principles Applied

### 1. Resource-Based URLs
- Each URL represents a resource
- Use plural nouns for collections
- Use IDs for specific resources

### 2. HTTP Methods
- `GET`: Read data
- `POST`: Create a new resource or perform an action
- `PATCH`: Partial update
- `PUT`: Full update (currently unused)
- `DELETE`: Delete a resource

### 3. Status Codes
- `200 OK`: Successful operation
- `201 Created`: Resource created
- `204 No Content`: Successful deletion
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required/failed
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found

### 4. Nested Resources
Dependent resources are defined as nested paths:
- `/boards/{id}/members/`: Members of a board
- `/boards/{id}/lists/`: Lists of a board
- `/tasks/{id}/comments/`: Comments of a task

### 5. Special Endpoints
- `/me/`: Access current user's resources
- `/public/`: Public resources

## Authentication
All endpoints require authentication except `/auth/register/` and `/auth/login/`.

### Headers
```
Authorization: Bearer <jwt_token>
```

## Response Format
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Error Format
```json
{
  "error": "Error message",
  "field_errors": {
    "field_name": ["Error detail"]
  }
}
```

## Pagination
Pagination is used for listing endpoints:
```
GET /api/v1/boards/?page=1&page_size=20
```

## Filtering & Sorting
```
GET /api/v1/tasks/?is_completed=false&priority=high&ordering=-created_at
```

## Notes
- The `/tasks/{id}/toggle-complete/` endpoint exists for better UX — a quick way to change completion state
- Completion status can be changed via PATCH (field `is_completed`) or via the toggle endpoint
- User limits are an independent resource, separate from boards
- Invitations are also managed as a top-level resource
