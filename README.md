# MagicPages
Magic Pages is e-commerce web application for book purchase.

## Purpose
The purpose of this project is to develop as a team project, the alternative to common book shops.

## Configuration (development)

* Clone this repository:

* Go to project directory and install requirements for development
```
cd MagicPages && pipenv install --dev && pipenv shell
```

* Create .env and fill with your environment variables configuration file from example config
```
cp config/.env.example config/.env
```

* Run development server:

```
./manage.py runserver
```

* Run celery (as bash script):

```
./run_celery.sh
```

## System dependencies

Python: *v3.8*

PostgreSQL: *v11*

Redis: *v5*
