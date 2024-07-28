# KeenIELTS Django Backend

This repository contains the Django backend for the KeenIELTS platform, which provides practice tests and resources for IELTS preparation.

## Table of Contents

- [URL](#url)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## URL

Visit our platform at [keenielts.com](https://keenielts.com)

## Features

- User authentication and authorization
- Practice tests management
- Leaderboard and performance tracking
- Integration with React frontend
- REST API for frontend communication
- Sitemap generation for better SEO
- **AI-powered evaluation**: Uses OpenAI for evaluating speaking and writing tests.
- **AI-generated feedback**: Provides daily feedback to help users track their performance.

## Tech Stack

- **Framework**: Django 3.1
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT (JSON Web Tokens)
- **Other Libraries**: 
  - `django_rest_framework`
  - `corsheaders`
  - `ckeditor`
  - `django-redis`
  - `openai`

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Redis

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/valanikevin/KeenIeltsDjango.git
   cd KeenIeltsDjango
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Copy and configure the sample configuration file:**

   ```bash
   cp sample-config.py config.py
   ```

   Update `config.py` with your secrets, email configuration, and database configuration.

5. **Set up the PostgreSQL database:**

   Create a database and update the `DATABASES` setting in `config.py`.

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'keenielts_db',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

6. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

7. **Create a superuser:**

   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

## Configuration

### Settings

- **`REACT_DOMAIN`**: The domain of the React frontend.
- **`SITE_ID`**: The ID of the current site (useful for Django's sites framework).
- **Caching**: Configured to use Redis.
- **JWT**: Configured for token-based authentication.
- **OpenAI**: Configure OpenAI API keys for evaluation features.

### Middleware

- Security middleware
- CORS middleware
- Session and authentication middleware
- Common middleware
- CSRF protection
- Message middleware
- Clickjacking protection

### Static and Media Files

- **Static Files**: Located in the `static` directory.
- **Media Files**: Located in the `media` directory.

## Usage

The Django backend serves as the API server for the KeenIELTS platform. It handles user authentication, test management, leaderboard updates, and more.

## API Endpoints

The primary API endpoints are defined in the `urls.py` file. Here are some key endpoints:

- `/sitemap.xml`: Generates a sitemap for SEO.
- `/api/auth/`: Authentication endpoints
- `/api/tests/`: Test management endpoints
- `/api/leaderboard/`: Leaderboard endpoints

### Included Apps

- **amrita**: Amrita module URLs
- **coachinginstitute**: Coaching institute module URLs
- **ieltstest**: IELTS test module URLs
- **leaderboard**: Leaderboard module URLs
- **student**: Student module URLs
- **custom_user**: Custom user module URLs
- **base**: Base module URLs

## Screenshots

Include screenshots of the application here to give users a visual overview.

![Screenshot 1](screenshots/screenshot1.png)
![Screenshot 2](screenshots/screenshot2.png)
![Screenshot 3](screenshots/screenshot3.png)

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

