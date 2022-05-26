from flask import Blueprint, render_template, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@auth.route('logout')
def logout():
    pass

@auth.route('/sign-up')
def sign_up():
    pass