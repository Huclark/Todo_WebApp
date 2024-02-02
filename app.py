from flask import Flask, render_template, request, redirect, url_for, flash, abort, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# __name__ just references the file
app = Flask(__name__)  # create a Flask application
# Secret key for form security
app.config['SECRET_KEY'] = 'b818346b8a50ca0f5e38dd6670a0b475'
# tell the app where our database is located (SQLite database URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# initialise our database
db = SQLAlchemy(app)
# initialise a Flask-login extension
login_manager = LoginManager(app)
# Specify the login view for Flask-Login
login_manager.login_view = 'login'

# create registration model
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password= PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit =SubmitField('Sign Up')

# create the login form 
# FlaskForm class is provided by FLASK-WTF   
# It saves you from writing these methods and properties from scratch
class LoginForm(FlaskForm):
    # Create a form field for the username
    # validators=[DataRequired()] specifies that the field is required
    username = StringField('Username', validators=[DataRequired()])
    # Create a form field for the password
    # validators=[DataRequired()] specifies that the field is required
    password = PasswordField('Password', validators=[DataRequired()])
    # create a submit button
    # Login is the label on the submit button
    submit = SubmitField('Login')

# create the User model
# UserMixin is a class which handles client authentication and sessions
class User(db.Model, UserMixin):
    """For users
    """
    # set the unique identifier of each user
    id = db.Column(db.Integer, primary_key=True)
    # Username for each user
    username = db.Column(db.String(120), unique=True, nullable=False)
    # hashed password of each user
    password_hash = db.Column(db.String(256), nullable=False)
    # this is a relationship attribut representing a one-to-many relationship with the 
    # Todo model. it links the user table to the todo table
    # each user can have multiple todo items
    # backref establishes a reverse relationship from Todo to User
    todos = db.relationship('Todo', backref='user', lazy=True)
    
    def __str__(self):
        """string representation of class"""
        return f"<User {self.id}>"
    
    def set_password(self, password):
        """This is used to set a hashed password

        Args:
            password (str): user password
        """
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Authenticates user password

        Args:
            password (str): plained-text password

        Returns:
            bool: true if password is authentic, otherwise false
        """
        # check_password_hash is from werkzeug library which safely verifies if 
        # a plained-text password is the same as a stored hashed password
        return check_password_hash(self.password_hash, password)

# create a class
class Todo(db.Model):
    """For the todo app 
    """
    # create columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __str__(self):
        """string representation of class"""
        return f"<Task {self.id}>"
    
# Flask-Login user loader
# The decorator below is used to register a callback function that loads a user given their
# user ID. A callback function is a function that is passed as an argument to another function
# and is intended to be called later. load_user is the callback function in this case
@login_manager.user_loader
def load_user(user_id):
    """Loads an existing user
    """
    return User.query.get(int(user_id))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successfull! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Login route
# decorator to define URL route for the login view
@app.route('/login', methods=['GET', 'POST'])
def login():
    # check if the user in the current session is authenticated
    if current_user.is_authenticated and request.method == 'POST':
        # redirect them to the home page
        return redirect(url_for('index'))
    # else create a form
    form = LoginForm()
    # validate_on_submit checks if the form has been submitted and is valid
    if form.validate_on_submit():
        # query the User model filtering through with the username from the form
        # if user is found user will hold an object of the User class with the specified username
        # if not found user will be none
        user = User.query.filter_by(username=form.username.data).first()
        # check if user exists and password is authentic;
        if user and user.check_password(form.password.data):
            # login_user from Flask-Login is used to login a user
            login_user(user)
            # Display a flash message
            flash('Login successful!', 'success')
            # redirect user to the index page
            return redirect(url_for('index'))
        # else if credentials are invalid, flash an error message
        flash('Invalid username or password', 'error')
    # redirect user to login page if credentials are invalid
    return render_template('login.html', form=form)

# Logout route
# decorator to define URL rout for the logout view
@app.route('/logout')
# decorator provided by Flask-Login to ensure user must be logged
# in to access the logout route. if user is not logged in and tries to
# access this page they will be redirected to the login page
@login_required
def logout():
    get_flashed_messages()
    # logout the user, a Flask-Login method
    logout_user()
    # flash logout message
    flash('Logout successful!', 'success')
    # redirect user to the login page
    return redirect(url_for('login'))
    
# create an index route so that when we browse to the URL we dont get error 404
@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    if request.method ==  "POST":
        # retrieve the content of the form
        # the 'content' passed to form is the name of the form in index.html
        task_content = request.form['content']
        # create a new task which is an instance of the Todo class
        new_task = Todo(content=task_content, user=current_user) # type: ignore
        
        try:
            # add task to database
            db.session.add(new_task)
            # commit it to the database
            db.session.commit()
            # return a redirect back to index
            return redirect('/')
        except:
            flash("There was an issue adding your task", "error")
    else:
        # Query the database to retrieve all the database ordered by their date-created
        tasks =Todo.query.filter_by(user=current_user).order_by(Todo.date_created).all()
        # render the home page which displays the todo lists
        return render_template("index.html", tasks=tasks)

# create another route for deleting a task
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    # retrieve the task by id and if it does not exist give an error 404
    delete_task = Todo.query.get_or_404(id)
    
    # Check if the task belongs to the current user
    if delete_task.user != current_user:
        # Forbidden, as the task does not belong to the current user
        abort(403)
    
    try:
        # delete task
        db.session.delete(delete_task)
        # commit the update
        db.session.commit()
        # redirect to task page
        return redirect('/')
    except:
        flash("There was an issue deleting your task", "error")
    
# create a route for updating an existing task
@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    # retrieve the task to update by id and if it does not exist give an error 404
    update_task= Todo.query.get_or_404(id)
    # Check if the task belongs to the current user
    if update_task.user != current_user:
        # Forbidden, as the task does not belong to the current user
        abort(403)
    if request.method == "POST":
        # update the content of the task
        update_task.content = request.form['content']
        
        try:
            # commit the update
            db.session.commit()
            # redirect to task page
            return redirect('/')
        except:
            flash("There was an issue updating your task", "error")
    else:
        return render_template("update.html", task=update_task)

if __name__ == "__main__":
    # create a context in which the app is active. it is a way
    # to execute code that needs access to the application context
    # such as database operations
    with app.app_context():
        # this creates all the tables defined in the SQLAlchemy models.
        # it initialises the database based on the models i have defined
        db.create_all()
        # Create a default user if there is none
        # this checks is there's no user with username, 'default' in the User table
        if not User.query.filter_by(username='default').first():
            default_user = User(username='default')
            default_user.set_password('taskmanager235802.')
            db.session.add(default_user)
            db.session.commit()
    # debug=True so when there is an error we can get a message to debug
    app.run(debug=True)
