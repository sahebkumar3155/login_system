from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret_key"

# mondodb
app.config["MONGO_URI"] = "mongodb://localhost:27017/user_db"
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})

    if login_user:
        if check_password_hash(login_user['password'], request.form['password']):
            session['username'] = request.form['username']
            return redirect(url_for('dashboard'))

    flash('Invalid username/password combination')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            hashpass = generate_password_hash(request.form['password'])
            users.insert_one({'username': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('dashboard'))

        flash('That username already exists!')
        return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        users = mongo.db.users.find()
        return render_template('dashboard.html', users=users)
    return redirect(url_for('home'))

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'username' in session:
        user = mongo.db.users.find_one({"_id": ObjectId(id)})

        if request.method == 'POST':
            mongo.db.users.update_one(
                {"_id": ObjectId(id)},
                {"$set": {
                    "username": request.form['username'],
                    "password": generate_password_hash(request.form['password'])
                }}
            )
            return redirect(url_for('dashboard'))

        return render_template('edit.html', user=user)

    return redirect(url_for('home'))

@app.route('/delete/<id>')
def delete(id):
    if 'username' in session:
        mongo.db.users.delete_one({"_id": ObjectId(id)})
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
