Arch Package Feed
=================

Provides a more advanced arch package feed.

*dependencies*:

  - python 3.2 or higher
  - bottle
  - sqlalchemy
  - feedparser
  - requests

Installation on Heroku
----------------------

1. Get the code and [the heroku toolbelt](https://toolbelt.heroku.com/)

```
$ wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
$ heroku login
$ git clone git://github.com/Mic92/arch-package-feed.git
```

2. Create the heroku app

```
$ cd arch-package-feed
$ heroku create
$ git push heroku master
```

3. Setup and promote the database

```
$ heroku addons:add heroku-postgresql:dev
Adding heroku-postgresql:dev to sushi... done,  v69 (free)
  Attached as HEROKU_POSTGRESQL_RED
Database has been created and is available
$ heroku config | grep HEROKU_POSTGRESQL
HEROKU_POSTGRESQL_RED_URL: postgres://user3123:passkja83kd8@ec2-117-21-174-214.compute-1.amazonaws.com:6212/db982398
$ heroku pg:promote HEROKU_POSTGRESQL_RED_URL # replace this with your url
```

Development
-----------

1. Get python 3, pip, virtualenv and the code

```
$ git clone git://github.com/Mic92/arch-package-feed.git
```

2. Setup virtualenv

```
$ virtualenv venv
$ . ./venv/bin/activate
$ pip install -r requirements.txt
```

3. Run the app (with sqlite)

```
$ DATABASE_URL=sqlite:///db.sqlite python app.py
Bottle v0.11.6 server starting up (using GunicornServer())...
Listening on http://0.0.0.0:3000/
```

You can control the host and port with HOST and PORT environment variable.
