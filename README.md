# MagicPages
Magic Pages is e-commerce web application for book purchase.

## Purpose
The purpose of this project is to develop as a team project, the alternative to common book shops.

## Configuration (development)

* Clone this repository:

* Go to project directory and install requirements for development
```
cd MagicPages && pipenv install --dev
```

* Create .env configuration file from example config
```
cp .env.example .env
```

* Enter local credentials for database and other ENV variables values:
```
nano .env
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
