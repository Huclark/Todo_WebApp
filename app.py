from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# __name__ just references the file
app = Flask(__name__)
# tell the app where our databse is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# initialise our database
db = SQLAlchemy(app)

# define a function to create the app
def create_app():
    with app.app_context():
        db.create_all()
    return app

# create a class
class Todo(db.Model):
    """For the todo app 
    """
    # create columns
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __str__(self):
        """string representation of class"""
        return f"<Task {self.id}>"    
    
# create an index route so that when we browse to the URL we dont get error 404
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method ==  "POST":
        # retrieve the content of the form
        # the 'content' passed to form is the name of the form in index.html
        task_content = request.form['content']
        # create a new task which is an instance of the Todo class
        new_task = Todo(content=task_content) # type: ignore
        
        try:
            # add task to database
            db.session.add(new_task)
            # commit it to the database
            db.session.commit()
            # return a redirect back to index
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        # Query the database to retrieve all the database ordered by their date-created
        tasks =Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks=tasks)
    
    return render_template("index.html")

if __name__ == "__main__":
    # debug=True so when there is an error we can get a message to debug
    app.run(debug=True)
