# Board Invitation Email System Setup

This document explains how to set up and use the board invitation email system with Celery and Django signals.

## Overview

The system automatically sends invitation emails when a `BoardInvitation` model is created using:
- **Django Signals**: Trigger email sending when invitation is created
- **Celery**: Handle asynchronous email sending
- **Redis**: Message broker for Celery
- **Email Templates**: HTML and text email templates

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Start Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### 3. Configure Email Settings

Update `core/settings.py` with your email provider settings:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your email
EMAIL_HOST_PASSWORD = 'your-app-password'  # Your app password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Site URL for email links
SITE_URL = 'http://localhost:8000'  # Update for production
```

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start Celery Worker

In a separate terminal:

```bash
cd /home/sina/trello_mini/trello_lite/core
celery -A core worker --loglevel=info
```

### 6. Start Django Development Server

```bash
python manage.py runserver
```

## Testing the System

### Method 1: Using Management Command

```bash
python manage.py test_invitation_email --email recipient@example.com
```

### Method 2: Using API

1. Create a board invitation via API:
```bash
curl -X POST http://localhost:8000/api/v1/boards/{board_id}/invite/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invited_email": "recipient@example.com",
    "role": "member"
  }'
```

2. The email will be sent automatically via Celery task.

### Method 3: Direct Model Creation

```python
from boards.models import BoardInvitation, Board
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

# Get existing board and user
board = Board.objects.first()
inviter = User.objects.first()

# Create invitation (triggers email automatically)
invitation = BoardInvitation.objects.create(
    board=board,
    invited_email='recipient@example.com',
    invited_by=inviter,
    role='member',
    expires_at=timezone.now() + timedelta(days=7)
)
```

## Email Flow

1. **Invitation Creation**: When `BoardInvitation` is created
2. **Signal Triggered**: `post_save` signal calls Celery task
3. **Email Sent**: Celery task renders templates and sends email
4. **User Clicks Link**: Email contains activation link
5. **Invitation Accepted**: User accepts via API endpoint

## API Endpoints

- **Create Invitation**: `POST /api/v1/boards/{board_id}/invite/`
- **View Invitation**: `GET /api/v1/boards/invitations/accept/{token}/`
- **Accept Invitation**: `POST /api/v1/boards/invitations/accept/{token}/`

## Email Templates

Templates are located in `templates/emails/`:
- `board_invitation.html`: HTML email template
- `board_invitation.txt`: Plain text email template

## Troubleshooting

### Celery Not Processing Tasks
- Check Redis is running: `redis-cli ping`
- Check Celery worker is running
- Check Celery logs for errors

### Emails Not Sending
- Verify email settings in `settings.py`
- Check email provider allows SMTP
- Use app passwords for Gmail
- Check Django logs for email errors

### Template Errors
- Ensure templates directory exists
- Check template syntax
- Verify context variables

## Production Considerations

1. **Use Environment Variables** for sensitive settings
2. **Configure Proper SMTP** server
3. **Set Correct SITE_URL** for production domain
4. **Use Supervisor** or similar for Celery process management
5. **Monitor Email Delivery** and handle failures
6. **Set Up Email Logging** for debugging

## Security Notes

- Invitation tokens are UUID4 (secure)
- Invitations expire after 7 days
- Email validation ensures correct recipient
- Authentication required for acceptance
