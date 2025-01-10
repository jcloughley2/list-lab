# List Lab

A Django web application that allows users to generate, manage, and share lists using OpenAI's LLM. Users can create lists, fork existing lists, and maintain their own collection of public and private lists.

## Features

- User authentication and registration
- List generation using OpenAI's LLM
- List management (create, edit, fork)
- Public and private list sharing
- User profiles with list collections
- List forking functionality

## Setup

1. Create and activate the virtual environment:
```bash
pyenv virtualenv 3.10.13 list-lab
pyenv activate list-lab
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_api_key_here
SECRET_KEY=your_django_secret_key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Technologies Used

- Django 5.1.4
- OpenAI API
- Python 3.10.13
- Bootstrap 5 (via crispy-bootstrap5)
- django-crispy-forms 