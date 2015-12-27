# spouk_bottle_peewee

Example usage
==============
use classical MVC pattern for split Models, Views, Controllers
type database need for use any model behavior for hook application.

mysql - add hook before/after for reconnect database each request,
beacause i hate fucken stupid retard error fucken `MySQL error 2006: mysql server has gone away`, 
stupid fucken Oracle.  Hate corporations.

psql - check each request exist database connection, if lost, reconnect. 

sqlite - nothing, very simple use. No need any tricks.


app.py
------
```python
    import bottle
    from bottle import request
    from spouk_bottle_peewee import DatabaseMiddleware
    from handlers import Handlers

    from models import dbobj

    app = bottle.Bottle()

    # wrapper app middle
    appdb = DatabaseMiddleware(app,db=dbobj.database,type_database='psql')

    hand = Handlers(app=app)

    # definition routing with callback 
    app.route('/', method=['get','post'], callback=hand.root)

    bottle.run(app=appdb, host='127.0.0.1', port=2000)
```

models.py
---------
```python
       
    from peewee import *
    from datetime import datetime
    from spouk_bottle_peewee import Database
    from config import DATABASE_PSQL

    dbobj = Database(DATABASE_PSQL, type_database='psql')

    class blog_cook(dbobj.Model):
        id = PrimaryKeyField()
        cookie = TextField()
        host = TextField()
        create = DateTimeField(default=datetime.today())
        dump_session = TextField()
        status = BooleanField()
        lastconnect = DateTimeField(datetime.today())
        lastip  = TextField()
        count_connection = IntegerField()
        userid = IntegerField()

    dbobj.blog_cook = blog_cook
```
config.py
---------
```python

DATABASE_PSQL = {
    'host': 'localhost',
    'name': 'session',
    'engine': 'playhouse.pool.PooledPostgresqlDatabase',
    'user': 'anonymous',
    'password': 'anonymous',
    'port': 5432,
}

```

handlers.py
------------
```python
    
from models import dbobj


class Handlers(object):
    def __init__(self, app=None):
        self.app = app
        self.db = dbobj
        
    def root(self):
        res = self.db.blog_cook.select()
        return self.app.render('index.html', result = res)
```

index.html
---------
```html
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<strong>Cookie table</strong>
<hr>
<table border=1>
        <thead>
        <tr>
            <th>id</th>
            <th>cookie</th>
            <th>host</th>
            <th>create</th>
            <th>dump</th>
            <th>status</th>
            <th>lastconnect</th>
            <th>lastip</th>
            <th>count_connect</th>
            <th>userid</th>
        </tr>
        </thead>
        <tbody>
        {% for p in result %}
        <tr>
            <td>{{ p.id }}</td>
            <td>{{ p.cookie }}</td>
            <td>{{ p.host}}</td>
            <td>{{ p.create }}</td>
            <td>{{ p.dump_session }}</td>
            <td>{{ p.status }}</td>
            <td>{{ p.lastconnect }}</td>
            <td>{{ p.lastip}}</td>
            <td>{{ p.count_connection }}</td>
            <td>{{ p.userid}}</td>

        </tr>
        {% endfor %}
        </tbody>
    </table>
```



