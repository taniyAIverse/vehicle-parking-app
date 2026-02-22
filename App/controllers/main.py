from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from  werkzeug.security import generate_password_hash, check_password_hash

from App import db
from App.models import User, Admin



main = Blueprint("main", __name__)

@main.route('/')
def home():
    return render_template("home.html")

@main.route("/signup", methods = ["GET", "POST"])
def signup(): 
    if request.method == "GET":
        return render_template("signup.html")

    elif request.method =="POST":
        username = request.form["username"].strip()
        name = request.form["name"]
        address = request.form["address"]
        pincode = request.form["pincode"]
        password = request.form["password"]
        confirm_pwd= request.form["Confirm-password"]
        
        user = User.query.filter_by(username=username).first()

        if user:
            flash("Username already exists!", "danger")
            return render_template("signup.html")
        if confirm_pwd != password :
            flash("Confirm Password and Password both must be same!", "danger")
            return render_template("signup.html")
        if len(pincode) != 6 :
            flash("Pincode must be a six digit number!", "danger")
            return render_template("signup.html")

   
        password= generate_password_hash(password)
        new_user = User(username=username, name=name, address=address, pincode=pincode, password=password)

        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please sign in.", "success")
        return redirect(url_for('main.signin'))
    else:
        flash("Something went wrong.", "danger")
        return render_template("signup.html")

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method== "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        admin = Admin.query.filter_by(username=username).first()
        if admin :
            verification= check_password_hash(admin.password, password)
            if verification:
                login_user(admin)
                return redirect(url_for('admin.admin_dashboard'))
            flash("Incorrect Password!", "danger")
            return redirect(url_for("main.signin"))

        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid Credentials! Try again.', "danger")
            return redirect(url_for("main.signin"))
        login_user(user)
        return redirect(url_for('user.user_dashboard'))
    else:
        flash("Something went wrong.", "danger")
        return render_template("signin.html")
    
@main.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))