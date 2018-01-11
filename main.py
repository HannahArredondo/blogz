from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import sys
from pprint import pprint
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheese@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "789sen&*("

#Defines the class, Blog and assigns the foreign key
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    entry = db.Column(db.String(500)) 
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,name,entry,owner):
        self.name = name
        self.entry = entry
        self.owner = owner


#Defines the class, User and links the foreign key.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref = "owner")

    def __init__(self,username,password):
        self.username = username
        self.password = password


#Verifies that the user is in session to access certain pages.
@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'sign_up', 'index', 'userpost', 'userposts']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


#If a name and blog entry is entered, a new blog is posted to the database. 
@app.route("/newpost", methods = ['POST','GET'])
def newpost():
    if request.method == 'POST':
        blog_name = request.form['name']
        blog_entry = request.form['entry']

        name_error = ""
        entry_error = ""

        if blog_name == "":
            name_error = "Please add a blog title."

        if blog_entry =="":
            entry_error = "Please add some content to the new blog post."
        
        if name_error or entry_error:
            return render_template("new_post.html", blog_name = blog_name, blog_entry = blog_entry, 
            name_error = name_error, entry_error = entry_error)
        
        else:
            owner = User.query.filter_by(username= session['username']).first()
            new_blog = Blog(blog_name, blog_entry, owner)
            db.session.add(new_blog)
            db.session.commit()

            return render_template("single_entry.html", blog = new_blog)

    return render_template("new_post.html", title = "CreatePost")


#Verifies someone's login information and redirects to the new blog page.
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

        elif not user:
            return render_template("log_in.html", error = "Oops! Username not valid.")    

        else:
            return render_template("log_in.html", error = "Oops! Try again!")

    return render_template("log_in.html")       


# Deletes current session and redirects to the list of all blogs. 
@app.route("/logout")
def logout():
    if session['username']:
        del session['username']
    return redirect('/blog')
    

#Registers a new user if the username is not already taken and the passwords match.
@app.route("/signup", methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        
        if password and not existing_user and password == verify and len(password)>2 and len(username)>3:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
        elif existing_user:
            return render_template("signup.html", error = "Name already in use. Please choose a different username.")

        elif len(username) < 3:
            return render_template("signup.html", error = "Username must be at least 3 characters.")
        
        elif not password:
            return render_template("signup.html",user_name = username, error = "Please enter a password.")

        elif len(password) < 3:
            return render_template("signup.html", error = "Password must be at least 3 characters.")

        else:
            return render_template("signup.html", user_name = username, error = "Passwords don't match.")
    else:
        return render_template("signup.html")


#If a name and blog entry is entered, a new blog is posted to the database. 
@app.route("/blog", methods=['POST', 'GET'])
def blog():
    is_blog_id = request.args.get('id')
    is_blog_user = request.args.get('user')
    
    if is_blog_id:
        single_blog = Blog.query.filter_by(id = is_blog_id).first()
        return render_template("single_entry.html", blog = single_blog)
    
    elif is_blog_user:
        the_user = User.query.filter_by( username = is_blog_user).first()
        user_blogs = Blog.query.filter_by( owner = the_user).all()
        return render_template("user_post.html", blogs = user_blogs, username= is_blog_user, title = "YourBlogs")    

    else:
        blogs = Blog.query.all()
        return render_template("blog.html", blogs = blogs, title = "YourBlogs")


#Displays all users in the database.
@app.route("/", methods = ['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template("index.html", users = users, title = "All Blogs")

if __name__ == "__main__":
    app.run()