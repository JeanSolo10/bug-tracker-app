from nis import cat
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Project, User
from . import db

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

# projects routing #
@views.route('/projects')
@login_required
def projects():
    return render_template("projects.html", user=current_user)

@views.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        owner_id = current_user.id
        members = request.form.getlist('members')

        if not name:
            flash('Enter name', category='error')
        elif not description:
            flash('Enter description', category='error')
        elif len(name) < 2:
            flash('Project Name must be greater than 1 character', category='error')
        elif len(name) < 4:
            flash('Project Description must be greater than 3 character', category='error')
        else:
            new_project = Project(name=name, description=description, owner_id=owner_id)
            db.session.add(new_project)
            # add members
            if members:
                for id in members:
                    member = User.query.filter_by(id=id).first()
                    new_project.members.append(member)
            db.session.commit()
            flash('Project created!', category='success')
            return redirect(url_for('views.projects'))

    # handle GET request
    users = load_all_users()
    return render_template("new_project.html", user=current_user, userList=users)    

@views.route('/projects/<id>/details', methods=['GET', 'POST'])
@login_required
def project_details(id):
    project = Project.query.filter_by(id=id)
    members = project[0].members

    return render_template("project_details.html", user=current_user, projects=project, members=members)

def load_all_users():
    return User.query.all()

# projects routing #