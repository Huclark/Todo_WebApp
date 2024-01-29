# app.py
```python
from flask import Flask, render_template, url_for

# __name__ just references the file
app = Flask(__name__)

# create an index route so that when we browse to the URL we dont get error 404
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # debug=True so when there is an error we can get a message to debug
    app.run(debug=True)
```

# layout.html
```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
        {% block head %}
        {% endblock %}
    </head>
    <body>
        {% block body %}{% endblock %}
    </body>
</html>
```

# index.html
```html
{% extends "layout.html" %}

{% block head %}
  
{% endblock %}

{% block body %}
  <h1>Template inheritance</h1>
{% endblock %}
```

# main.css
```css
body {
    margin: 0;
    font-family: sans-serif;
}
```

# Launching database

- On terminal type `source env/bin/activate` to set the environment
- Run `python3` terminal
- follow this:
```python
from app import create_app, db

# create the FLask app instance
app = create_app()

# Use the app context
with app.app_context():
    # Create all tables
    db.create_all()
```
