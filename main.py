from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cheese@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "789sen&*("

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    entry = db.Column(db.String(500))

    def __init__(self,name,entry):
        self.name = name
        self.entry = entry

@app.route("/newpost", methods = ['POST','GET'])
def newpost():
    
    if request.method == "POST":
        name = request.form['name']
        entry = request.form['entry']
        new_blog = Blog(name, entry)
        db.session.add(new_blog)
        db.session.commit()

    return render_template("new_post.html", title = "CreatePost")

@app.route("/blog", methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        blog_name= request.form['name']
        blog_entry= request.form['entry']
        print(blog_name, blog_entry)
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
            new_blog = Blog(blog_name, blog_entry)
            db.session.add(new_blog)
            db.session.commit()

            return render_template("single_entry.html", blog = new_blog)

    else:
        is_blog_id = request.args.get('id')
        if is_blog_id:
            single_blog = Blog.query.filter_by(id = is_blog_id).first()
            return render_template("single_entry.html", blog = single_blog)
        else:
            blogs = Blog.query.all()
            return render_template("blog.html", blogs = blogs, title = "YourBlogs")


if __name__ == "__main__":
    app.run()