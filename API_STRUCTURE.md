# Trello Lite REST API Structure

## Overview
این پروژه از معماری RESTful برای طراحی API استفاده می‌کند. تمام endpoints ها بر اساس استانداردهای REST طراحی شده‌اند.

## Base URL
```
https://your-domain.com/api/v1/
```

## API Resources

### 1. Authentication (`/auth/`)
منابع مربوط به احراز هویت به صورت مستقل از user management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | ثبت‌نام کاربر جدید |
| POST | `/auth/login/` | ورود (دریافت JWT token) |
| POST | `/auth/refresh/` | تازه‌سازی token |
| POST | `/auth/logout/` | خروج |
| POST | `/auth/password/reset/` | درخواست بازیابی رمز عبور |
| POST | `/auth/password/reset/confirm/` | تایید بازیابی رمز عبور |
| POST | `/auth/verify-email/` | تایید ایمیل |

### 2. Users (`/users/`)
مدیریت کاربران سیستم.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | لیست کاربران (فقط admin) |
| GET | `/users/me/` | اطلاعات کاربر جاری |
| GET | `/users/{id}/` | اطلاعات کاربر خاص |
| PATCH | `/users/me/` | ویرایش کاربر جاری |
| PATCH | `/users/{id}/` | ویرایش کاربر خاص (admin) |
| DELETE | `/users/{id}/` | حذف کاربر |
| POST | `/users/me/password/` | تغییر رمز عبور کاربر جاری |
| POST | `/users/{id}/password/` | تغییر رمز عبور کاربر خاص |

### 3. Profiles (`/profiles/`)
مدیریت پروفایل کاربران به عنوان منبع مستقل.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profiles/` | لیست پروفایل‌ها |
| GET | `/profiles/me/` | پروفایل کاربر جاری |
| GET | `/profiles/{id}/` | پروفایل کاربر خاص |
| PATCH | `/profiles/me/` | ویرایش پروفایل کاربر جاری |
| PATCH | `/profiles/{id}/` | ویرایش پروفایل کاربر خاص |

### 4. Boards (`/boards/`)
مدیریت بردها و منابع وابسته.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/` | لیست بردهای کاربر |
| POST | `/boards/` | ایجاد برد جدید |
| GET | `/boards/{id}/` | جزئیات برد |
| PATCH | `/boards/{id}/` | ویرایش برد |
| DELETE | `/boards/{id}/` | حذف برد |
| GET | `/boards/public/` | لیست بردهای عمومی |

#### Nested Resources - Members
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/{board_id}/members/` | لیست اعضای برد |
| DELETE | `/boards/{board_id}/members/{user_id}/` | حذف عضو از برد |

#### Nested Resources - Invitations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/{board_id}/invitations/` | لیست دعوت‌نامه‌های برد |
| POST | `/boards/{board_id}/invitations/` | ارسال دعوت‌نامه جدید |
| POST | `/boards/{board_id}/invitations/user/` | دعوت کاربر ثبت‌نام شده |

#### Board Actions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/boards/{board_id}/leave/` | خروج از برد |
| GET | `/boards/{board_id}/activities/` | تاریخچه فعالیت‌های برد |

#### Nested Resources - Lists
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/boards/{board_id}/lists/` | لیست‌های برد |
| POST | `/boards/{board_id}/lists/` | ایجاد لیست جدید |

### 5. Lists (`/lists/`)
مدیریت لیست‌ها.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/lists/{id}/` | جزئیات لیست |
| PATCH | `/lists/{id}/` | ویرایش لیست |
| DELETE | `/lists/{id}/` | حذف لیست |
| POST | `/lists/{id}/move/` | جابجایی لیست |

### 6. Tasks (`/tasks/`)
مدیریت وظایف.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/` | وظایف اختصاص داده شده به کاربر |
| GET | `/tasks/{id}/` | جزئیات وظیفه |
| PATCH | `/tasks/{id}/` | ویرایش وظیفه |
| DELETE | `/tasks/{id}/` | حذف وظیفه |
| POST | `/tasks/{id}/move/` | جابجایی وظیفه |
| POST | `/tasks/{id}/toggle-complete/` | تغییر سریع وضعیت تکمیل |

#### Nested Resources - Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/{task_id}/comments/` | لیست نظرات |
| POST | `/tasks/{task_id}/comments/` | ایجاد نظر جدید |
| GET | `/tasks/{task_id}/comments/{id}/` | جزئیات نظر |
| PATCH | `/tasks/{task_id}/comments/{id}/` | ویرایش نظر |
| DELETE | `/tasks/{task_id}/comments/{id}/` | حذف نظر |

#### List-specific Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/lists/{list_id}/` | وظایف یک لیست |
| POST | `/tasks/lists/{list_id}/` | ایجاد وظیفه در لیست |

### 7. Invitations (`/invitations/`)
مدیریت دعوت‌نامه‌های کاربر.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/invitations/` | دعوت‌نامه‌های کاربر |
| GET | `/invitations/{id}/` | جزئیات دعوت‌نامه |
| POST | `/invitations/{id}/respond/` | پاسخ به دعوت‌نامه (accept/reject) |

### 8. User Limits (`/limits/`)
محدودیت‌های کاربر.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/limits/` | محدودیت‌های کاربر جاری |
| GET | `/limits/{user_id}/` | محدودیت‌های کاربر خاص (admin) |

## REST Principles Applied

### 1. Resource-Based URLs
- هر URL نماینده یک منبع (resource) است
- استفاده از اسامی جمع برای collections
- استفاده از IDs برای منابع خاص

### 2. HTTP Methods
- `GET`: خواندن داده‌ها
- `POST`: ایجاد منبع جدید یا انجام عملیات
- `PATCH`: به‌روزرسانی جزئی
- `PUT`: به‌روزرسانی کامل (در حال حاضر استفاده نمی‌شود)
- `DELETE`: حذف منبع

### 3. Status Codes
- `200 OK`: عملیات موفق
- `201 Created`: ایجاد منبع جدید
- `204 No Content`: حذف موفق
- `400 Bad Request`: خطای validation
- `401 Unauthorized`: عدم احراز هویت
- `403 Forbidden`: عدم دسترسی
- `404 Not Found`: منبع یافت نشد

### 4. Nested Resources
منابع وابسته به صورت nested تعریف شده‌اند:
- `/boards/{id}/members/`: اعضای یک برد
- `/boards/{id}/lists/`: لیست‌های یک برد
- `/tasks/{id}/comments/`: نظرات یک وظیفه

### 5. Special Endpoints
- `/me/`: برای دسترسی به منابع کاربر جاری
- `/public/`: برای منابع عمومی

## Authentication
تمام endpoints ها به جز `/auth/register/` و `/auth/login/` نیاز به احراز هویت دارند.

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
برای لیست‌ها از pagination استفاده می‌شود:
```
GET /api/v1/boards/?page=1&page_size=20
```

## Filtering & Sorting
```
GET /api/v1/tasks/?is_completed=false&priority=high&ordering=-created_at
```

## Notes
- endpoint `/tasks/{id}/toggle-complete/` برای UX بهتر اضافه شده - راه سریع برای تغییر وضعیت تکمیل
- تغییر completion status هم از طریق PATCH endpoint با فیلد `is_completed` و هم از طریق toggle endpoint امکان‌پذیر است
- محدودیت‌های کاربر به صورت منبع مستقل از boards جدا شده است
- دعوت‌نامه‌ها هم به صورت منبع مستقل قابل مدیریت هستند
