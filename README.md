# MagicPages
Web application for book purchase

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


## System dependencies

Python: *v3.8*

PostgreSQL: *v11*
