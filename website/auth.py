from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import types

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    currForm = types.SimpleNamespace()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # keep values already filled in form
        if email:
            currForm.email = email

        user = User.query.filter_by(email=email).first()

        if user: 
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            if not email:
                flash('Please enter your email!', category='error')
            elif not password:
                flash('Please enter your password!', category='error')    
            else:
                flash('Email does not exist.', category='error')


    return render_template("login.html", user=current_user, form=currForm)

@auth.route('logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    currForm = types.SimpleNamespace()
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        role = request.form.getlist('role')[0]
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # keep values already filled in form
        if email:
            currForm.email = email
        if first_name:
            currForm.first_name = first_name
        if last_name:
            currForm.last_name = last_name
        if role:
            currForm.role = role

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists!', category='error')
        elif not email:
            flash('You must enter an email!', category='error')
        elif not first_name:
            flash('You must enter your first name!', category='error')
        elif not last_name:
            flash('You must enter your last name!', category='error')
        elif role == 'Select Role':
            flash('You must select a role', category='error')
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('First Name must be greater than 1 character', category='error')
        elif len(last_name) < 2:
            flash('Last Name must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, role=role, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            login_user(new_user, remember=True)
            # blueprint (router) + function name
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user, form=currForm)